from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "producer", "unit_price", "quantity", "unit")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total", "created_at")
    list_filter = ("status",)
    search_fields = ("customer__first_name", "customer__email")
    inlines = [OrderItemInline]
