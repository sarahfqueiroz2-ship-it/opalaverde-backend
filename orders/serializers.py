from django.db import transaction
from rest_framework import serializers

from catalog.models import Product

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    producer_name = serializers.CharField(source="producer.first_name", read_only=True)
    producer_whatsapp = serializers.CharField(
        source="producer.producer_profile.whatsapp", read_only=True, default=""
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "producer",
            "producer_name",
            "producer_whatsapp",
            "unit_price",
            "quantity",
            "unit",
            "subtotal",
        ]
        read_only_fields = ["product_name", "producer", "unit_price", "unit"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.first_name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_phone",
            "status",
            "delivery_address",
            "total",
            "delivery_fee",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["customer", "total", "created_at", "updated_at"]


class CheckoutItemSerializer(serializers.Serializer):
    """Um item enviado pelo cliente no momento de finalizar o pedido."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(active=True))
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    """
    Recebe a lista de produtos do carrinho e cria o pedido.
    O preço de cada item é sempre lido do banco (Product.price),
    nunca confiamos em um preço enviado pelo front-end.
    """

    items = CheckoutItemSerializer(many=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("O carrinho está vazio.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data["items"]

        order = Order.objects.create(
            customer=request.user,
            delivery_address=validated_data.get("delivery_address", ""),
            notes=validated_data.get("notes", ""),
        )

        subtotal = 0
        for item in items_data:
            product = item["product"]
            quantity = item["quantity"]

            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Estoque insuficiente para '{product.name}' "
                    f"(disponível: {product.stock})."
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                producer=product.producer,
                unit_price=product.price,
                quantity=quantity,
                unit=product.unit,
            )
            product.stock -= quantity
            product.save(update_fields=["stock"])
            subtotal += product.price * quantity

        order.total = subtotal + order.delivery_fee
        order.save(update_fields=["total"])
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
