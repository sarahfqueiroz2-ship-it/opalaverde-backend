from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, FavoriteViewSet, ProductImageViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("favorites", FavoriteViewSet, basename="favorite")
router.register("product-images", ProductImageViewSet, basename="product-image")

urlpatterns = router.urls
