from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Qualquer pessoa pode ler as avaliações de um produto.
    Só clientes autenticados podem criar (uma avaliação por produto).
    O produtor dono do produto pode responder (ação 'reply').
    """

    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("customer", "product")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product"]

    def get_permissions(self):
        if self.action in ("create", "reply"):
            return [permissions.IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """Lista as avaliações de todos os produtos do produtor autenticado."""
        reviews = Review.objects.filter(product__producer=request.user).select_related(
            "customer", "product"
        )
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def reply(self, request, pk=None):
        """O produtor dono do produto responde a uma avaliação."""
        review = self.get_object()
        if request.user != review.product.producer and request.user.user_type != "admin":
            return Response(
                {"detail": "Só o produtor do item pode responder esta avaliação."},
                status=status.HTTP_403_FORBIDDEN,
            )
        review.producer_reply = request.data.get("producer_reply", "")
        review.save(update_fields=["producer_reply"])
        return Response(ReviewSerializer(review).data)
