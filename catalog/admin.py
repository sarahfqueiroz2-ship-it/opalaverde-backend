from django.contrib import admin

from .models import Category, Favorite, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "priority", "status", "product_count")
    list_filter = ("status", "priority")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "producer", "category", "price", "stock", "active")
    list_filter = ("active", "category")
    search_fields = ("name", "producer__first_name")
    inlines = [ProductImageInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
