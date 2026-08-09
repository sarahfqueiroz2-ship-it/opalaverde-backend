from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import Product


class Order(models.Model):
    """
    Pedido feito por um cliente. Pode conter produtos de vários produtores;
    cada OrderItem sabe qual produtor vendeu aquele item, permitindo que
    cada produtor veja só os itens dele.
    """

    class Status(models.TextChoices):
        RECEBIDO = "received", "Recebido"
        PREPARANDO = "preparing", "Preparando"
        PRONTO = "ready", "Pronto"
        ENTREGUE = "delivered", "Entregue"
        CANCELADO = "cancelled", "Cancelado"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.RECEBIDO
    )
    delivery_address = models.CharField(max_length=255, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("5.00"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer}"

    def recalculate_total(self):
        subtotal = sum(item.subtotal for item in self.items.all())
        self.total = subtotal + self.delivery_fee
        self.save(update_fields=["total"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="order_items"
    )
    # "Fotografia" dos dados no momento da compra (o produto pode mudar depois)
    product_name = models.CharField(max_length=150)
    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sold_order_items",
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=20, blank=True)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
