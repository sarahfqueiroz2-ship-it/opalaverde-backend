from rest_framework import serializers

from .models import Review


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

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)
