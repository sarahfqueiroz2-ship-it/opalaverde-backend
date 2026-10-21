from rest_framework import serializers

from .models import Review
from orders.models import OrderItem, Order


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.first_name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "product_name",
            "customer",
            "customer_name",
            "rating",
            "comment",
            "producer_reply",
            "created_at",
        ]
        read_only_fields = ["customer", "producer_reply", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product", getattr(self.instance, "product", None))
        if not user.is_authenticated or user.user_type != "cliente":
            raise serializers.ValidationError("Somente clientes podem avaliar.")
        if not OrderItem.objects.filter(order__customer=user, order__status=Order.Status.ENTREGUE, order__payment_status=Order.PaymentStatus.PAID, product=product).exists():
            raise serializers.ValidationError("Avalie somente produtos de compras concluídas e pagas.")
        return attrs

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)
