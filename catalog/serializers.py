from rest_framework import serializers

from .models import Category, Favorite, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "priority",
            "status",
            "product_count",
            "created_at",
        ]
        read_only_fields = ["slug", "created_at"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "order"]


class ProductImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "order"]


class ProductSerializer(serializers.ModelSerializer):
    """Usado tanto na listagem do catálogo quanto no detalhe do produto."""

    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True, default="")
    producer_name = serializers.CharField(source="producer.first_name", read_only=True)
    producer_location = serializers.CharField(
        source="producer.producer_profile.farm_location", read_only=True, default=""
    )
    producer_bio = serializers.CharField(
        source="producer.producer_profile.bio", read_only=True, default=""
    )
    rating_average = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "producer",
            "producer_name",
            "producer_location",
            "producer_bio",
            "category",
            "category_name",
            "category_slug",
            "name",
            "description",
            "price",
            "unit",
            "stock",
            "specs",
            "active",
            "images",
            "rating_average",
            "rating_count",
            "is_favorited",
            "created_at",
        ]
        read_only_fields = ["producer", "created_at"]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, product=obj).exists()

    def create(self, validated_data):
        # O produtor dono do produto é sempre o usuário autenticado
        validated_data["producer"] = self.context["request"].user
        return super().create(validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "product", "product_detail", "created_at"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
