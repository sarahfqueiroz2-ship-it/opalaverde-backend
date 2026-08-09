from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    - Cliente: vê e cria só os próprios pedidos (checkout).
    - Produtor: vê os pedidos que contêm pelo menos um produto dele
      (ação 'received') e pode atualizar o status.
    - Admin: vê todos os pedidos.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "admin":
            return Order.objects.all().prefetch_related("items")
        if user.user_type == "produtor":
            return (
                Order.objects.filter(items__producer=user)
                .distinct()
                .prefetch_related("items")
            )
        return Order.objects.filter(customer=user).prefetch_related("items")

    def get_serializer_class(self):
        if self.action == "checkout":
            return CheckoutSerializer
        return OrderSerializer

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Finaliza o pedido a partir dos itens do carrinho."""
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        """
        Produtor/admin atualiza o status do pedido
        (recebido -> preparando -> pronto -> entregue, ou cancelado).
        """
        order = self.get_object()
        new_status = request.data.get("status")
        valid_statuses = dict(Order.Status.choices)

        if new_status not in valid_statuses:
            return Response(
                {"detail": "Status inválido."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        is_owner_producer = order.items.filter(producer=user).exists()
        is_owner_customer = order.customer_id == user.id

        if user.user_type == "admin" or is_owner_producer:
            pass  # admin e produtor dono de algum item podem mudar para qualquer status
        elif is_owner_customer and new_status == Order.Status.CANCELADO:
            pass  # cliente só pode cancelar o próprio pedido
        else:
            return Response(
                {"detail": "Você não tem permissão para alterar este pedido."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.status = new_status
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)
