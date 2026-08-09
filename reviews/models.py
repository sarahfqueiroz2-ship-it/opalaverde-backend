from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from catalog.models import Product


class Review(models.Model):
    """Avaliação de um produto feita por um cliente que comprou."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    producer_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "customer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}★ - {self.product} por {self.customer}"
