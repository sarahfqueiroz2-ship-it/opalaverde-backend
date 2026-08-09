from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Favorite, Product, ProductImage
from .permissions import IsAdminUserType, IsProducerOwnerOrAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    FavoriteSerializer,
    ProductImageUploadSerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Categorias do catálogo. Qualquer pessoa pode ver;
    só o admin pode criar/editar/apagar.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUserType()]
        return [permissions.AllowAny()]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Produtos do catálogo. Qualquer pessoa pode ver produtos ativos;
    o produtor só pode criar/editar/apagar os próprios produtos.
    """

    serializer_class = ProductSerializer
    permission_classes = [IsProducerOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "producer", "active"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        queryset = Product.objects.select_related("producer", "category").prefetch_related(
            "images"
        )
        # Por padrão, quem não é o dono/admin só vê produtos ativos
        if self.action in ("list", "retrieve"):
            user = self.request.user
            if not (user.is_authenticated and user.user_type in ("produtor", "admin")):
                queryset = queryset.filter(active=True)
        return queryset

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """Lista só os produtos do produtor autenticado (tela 'Meus Produtos')."""
        products = Product.objects.filter(producer=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Lista de favoritos do cliente autenticado."""

    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Upload e exclusão de fotos de produto. Só o produtor dono do produto
    (ou admin) pode enviar/apagar imagens dele.
    """

    serializer_class = ProductImageUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "delete", "head", "options"]

    def get_queryset(self):
        if self.request.user.user_type == "admin":
            return ProductImage.objects.all()
        return ProductImage.objects.filter(product__producer=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")
        user = self.request.user
        if user.user_type != "admin" and product.producer_id != user.id:
            raise permissions.PermissionDenied(
                "Você só pode enviar fotos para os seus próprios produtos."
            )
        serializer.save()
