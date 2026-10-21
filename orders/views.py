from django.db.models import Q
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import PermissionDenied
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

    def perform_update(self, serializer):
        raise PermissionDenied("Use as ações de status e pagamento.")

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Finaliza o pedido a partir dos itens do carrinho."""
        if request.user.user_type != "cliente":
            return Response({"detail": "Somente clientes podem finalizar pedidos."}, status=403)
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

        if user.user_type == "admin" or (is_owner_producer and not order.items.exclude(producer=user).exists()):
            pass  # admin e produtor dono de algum item podem mudar para qualquer status
        elif is_owner_customer and new_status == Order.Status.CANCELADO:
            pass  # cliente só pode cancelar o próprio pedido
        else:
            return Response(
                {"detail": "Você não tem permissão para alterar este pedido."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.status == Order.Status.CANCELADO and new_status != Order.Status.CANCELADO:
            return Response({"detail": "Pedido cancelado não pode ser reaberto."}, status=400)
        if order.status == Order.Status.ENTREGUE and new_status == Order.Status.CANCELADO:
            return Response({"detail": "Pedido entregue exige tratamento manual de devolução."}, status=400)
        if new_status == Order.Status.ENTREGUE and order.payment_status != Order.PaymentStatus.PAID:
            return Response({"detail": "Confirme o pagamento antes de marcar como entregue."}, status=400)
        # A justificativa é obrigatória para toda recusa/cancelamento novo.
        cancellation_reason = str(request.data.get("cancellation_reason") or "").strip()
        if new_status == Order.Status.CANCELADO and order.status != Order.Status.CANCELADO:
            if len(cancellation_reason) < 10:
                return Response({"detail": "Informe o motivo da recusa/cancelamento (mínimo de 10 caracteres)."}, status=400)
            if len(cancellation_reason) > 1000:
                return Response({"detail": "O motivo deve ter até 1000 caracteres."}, status=400)
            with transaction.atomic():
                order = Order.objects.select_for_update().get(pk=order.pk)
                from catalog.models import Product
                for item in order.items.select_related("product"):
                    # Estoque só é reservado após confirmação de pagamento.
                    if order.payment_status == Order.PaymentStatus.PAID and item.product_id:
                        Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)
                order.status = new_status
                order.cancellation_reason = cancellation_reason
                order.save(update_fields=["status", "cancellation_reason"])
        else:
            order.status = new_status
            order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["patch"])
    def payment(self, request, pk=None):
        order = self.get_object()
        if request.user.user_type != "admin" and (not order.items.filter(producer=request.user).exists() or order.items.exclude(producer=request.user).exists()):
            return Response({"detail": "Somente o produtor envolvido ou administrador pode confirmar pagamento."}, status=403)
        new_status = request.data.get("payment_status")
        if new_status not in (Order.PaymentStatus.AGREED, Order.PaymentStatus.PAID):
            return Response({"detail": "Situação de pagamento inválida."}, status=400)
        if order.status == Order.Status.CANCELADO:
            return Response({"detail": "Pedido cancelado."}, status=400)
        method = str(request.data.get("payment_method", order.payment_method)).strip()[:60]
        if not method:
            return Response({"detail": "Informe a forma de pagamento combinada."}, status=400)
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            if order.status == Order.Status.CANCELADO:
                return Response({"detail": "Pedido cancelado."}, status=400)
            if order.payment_status == Order.PaymentStatus.PAID and new_status != Order.PaymentStatus.PAID:
                return Response({"detail": "Pagamento confirmado não pode voltar a combinado."}, status=400)
            if new_status == Order.PaymentStatus.PAID and order.payment_status != Order.PaymentStatus.AGREED:
                return Response({"detail": "Combine primeiro o pagamento com o cliente."}, status=400)
            if new_status == Order.PaymentStatus.PAID and order.payment_status != Order.PaymentStatus.PAID:
                from catalog.models import Product
                for item in order.items.select_related("product"):
                    if not item.product_id:
                        return Response({"detail": "Produto removido. Não é possível confirmar."}, status=400)
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    if product.stock < item.quantity:
                        return Response({"detail": f"Estoque insuficiente para {item.product_name}."}, status=400)
                    product.stock -= item.quantity
                    product.save(update_fields=["stock"])
            order.payment_method = method
            order.payment_status = new_status
            order.save(update_fields=["payment_method", "payment_status"])
        return Response(OrderSerializer(order).data)
