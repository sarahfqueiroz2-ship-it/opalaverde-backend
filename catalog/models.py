from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Categoria de produto, com suporte a subcategorias (parent),
    igual ao que a tela de gestão de categorias do admin já projetava.
    """

    class Priority(models.TextChoices):
        LOW = "low", "Baixa"
        MEDIUM = "medium", "Média"
        HIGH = "high", "Alta"

    class Status(models.TextChoices):
        ACTIVE = "active", "Ativa"
        INACTIVE = "inactive", "Inativa"

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        return self.products.filter(active=True).count()


class Product(models.Model):
    """Produto vendido por um produtor no catálogo."""

    class Unit(models.TextChoices):
        UNIDADE = "unidade", "Unidade"
        KG = "kg", "Quilo (kg)"
        MACO = "maço", "Maço"
        DUZIA = "dúzia", "Dúzia"
        LITRO = "litro", "Litro"

    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"user_type": "produtor"},
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.UNIDADE)
    stock = models.PositiveIntegerField(default=0)
    specs = models.JSONField(default=dict, blank=True)  # ex: {"Peso médio": "200-300g"}
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def rating_average(self):
        agg = self.reviews.aggregate(models.Avg("rating"))
        return round(agg["rating__avg"] or 0, 1)

    @property
    def rating_count(self):
        return self.reviews.count()


class ProductImage(models.Model):
    """Imagens de um produto (a primeira cadastrada é a capa)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Imagem de {self.product.name}"


class Favorite(models.Model):
    """Produto favoritado por um cliente."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
