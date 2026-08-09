from rest_framework import permissions


class IsAdminUserType(permissions.BasePermission):
    """Permite acesso apenas a usuários com user_type == 'admin'."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "admin"
        )


class IsProducerOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Qualquer pessoa pode ler (GET). Para criar/editar/apagar um produto,
    é preciso ser o produtor dono do produto ou um admin.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.user_type in ("produtor", "admin")
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.user_type == "admin":
            return True
        return obj.producer_id == request.user.id
