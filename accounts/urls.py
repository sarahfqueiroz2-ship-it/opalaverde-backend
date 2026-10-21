from .site_config_api import site_configuration, public_site_configuration
from .admin_api import overview
from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import ClientAddressViewSet, MeView, ProducerProfileView, RegisterView

router = DefaultRouter()
router.register("addresses", ClientAddressViewSet, basename="address")

urlpatterns = [
    path("admin-site-settings/", site_configuration, name="admin-site-settings"),
    path("site-settings/public/", public_site_configuration, name="public-site-settings"),
    path("admin-overview/", overview, name="admin-overview"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("producer-profile/", ProducerProfileView.as_view(), name="producer-profile"),
] + router.urls
