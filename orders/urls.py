from rest_framework.routers import DefaultRouter

from .views import OrderViewSet
from .chat import ConversationViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

router.register("conversations", ConversationViewSet, basename="conversation")

urlpatterns = router.urls
