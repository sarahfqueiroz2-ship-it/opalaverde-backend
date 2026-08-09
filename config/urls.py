"""
URL raiz do backend do OpalaVerde.

Estrutura da API:
  /admin/                     -> painel administrativo padrão do Django
  /api/auth/token/            -> login (retorna access + refresh JWT)
  /api/auth/token/refresh/    -> renovar o access token
  /api/accounts/register/     -> cadastro de cliente/produtor
  /api/accounts/me/           -> dados do usuário autenticado
  /api/accounts/addresses/    -> endereços do cliente
  /api/catalog/categories/    -> categorias
  /api/catalog/products/      -> produtos (?category=&search=&producer=)
  /api/catalog/products/mine/ -> produtos do produtor autenticado
  /api/catalog/favorites/     -> favoritos do cliente autenticado
  /api/orders/orders/         -> pedidos (cliente vê os seus, produtor vê os que tem itens dele)
  /api/orders/orders/checkout/-> finalizar pedido a partir do carrinho
  /api/reviews/reviews/       -> avaliações de produtos (?product=)
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import CustomTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/accounts/", include("accounts.urls")),
    path("api/catalog/", include("catalog.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/reviews/", include("reviews.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
