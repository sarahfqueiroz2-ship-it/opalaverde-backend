from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import ClientAddressViewSet, MeView, ProducerProfileView, RegisterView

router = DefaultRouter()
router.register("addresses", ClientAddressViewSet, basename="address")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("producer-profile/", ProducerProfileView.as_view(), name="producer-profile"),
] + router.urls
