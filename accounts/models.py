from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Usuário customizado do OpalaVerde.
    O login é feito por e-mail (não por username), e cada usuário tem um tipo:
    cliente, produtor ou admin.
    """

    class UserType(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        PRODUTOR = "produtor", "Produtor"
        ADMIN = "admin", "Administrador"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField("Foto de perfil", upload_to="avatars/", blank=True, null=True)
    user_type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.CLIENTE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"


class ProducerProfile(models.Model):
    """
    Dados extras do produtor/fornecedor, preenchidos no cadastro
    (nome da fazenda/sítio, localização, certificação etc.)
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="producer_profile"
    )
    farm_name = models.CharField("Nome da fazenda/sítio", max_length=150, blank=True)
    farm_location = models.CharField("Localização", max_length=150, blank=True)
    farm_size = models.CharField("Tamanho da propriedade", max_length=50, blank=True)
    certification = models.CharField("Certificação", max_length=100, blank=True)
    products_type = models.CharField("Tipo de produtos", max_length=100, blank=True)
    bio = models.TextField("Sobre o produtor", blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=20, blank=True)
    address = models.CharField("Endereço completo", max_length=255, blank=True)

    def __str__(self):
        return self.farm_name or f"Perfil de {self.user}"


class ClientAddress(models.Model):
    """Endereço de entrega do cliente (usado no checkout)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField("Rótulo (Casa, Trabalho...)", max_length=50, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    street = models.CharField(max_length=200, blank=True)
    number = models.CharField(max_length=20, blank=True)
    complement = models.CharField(max_length=100, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_default", "-id"]

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}/{self.state}"
