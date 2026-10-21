from decimal import Decimal
from django.db.models import Sum, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import User
from catalog.models import Product, Category
from orders.models import Order

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def overview(request):
    if request.user.user_type != "admin" or not request.user.is_active:
        return Response({"detail": "Acesso restrito ao administrador."}, status=403)
    paid = Order.objects.filter(payment_status=Order.PaymentStatus.PAID).exclude(status=Order.Status.CANCELADO)
    return Response({
        "users": User.objects.count(),
        "clients": User.objects.filter(user_type="cliente").count(),
        "producers": User.objects.filter(user_type="produtor").count(),
        "products": Product.objects.count(),
        "active_products": Product.objects.filter(active=True).count(),
        "categories": Category.objects.count(),
        "orders": Order.objects.count(),
        "paid_orders": paid.count(),
        "pending_orders": Order.objects.exclude(status__in=[Order.Status.ENTREGUE, Order.Status.CANCELADO]).count(),
        "revenue_confirmed": str(paid.aggregate(total=Sum("total"))["total"] or Decimal("0.00")),
        "users_list": list(User.objects.order_by("-id").values("id", "username", "email", "first_name", "last_name", "user_type", "is_active")[:500]),
        "orders_list": list(Order.objects.select_related("customer").order_by("-created_at").values("id", "customer__username", "status", "payment_status", "total", "created_at")[:500]),
    })
