from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Редактировать объект может только владелец или сотрудник."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'owner', None) == request.user or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Чтение доступно пользователям, изменение - только администраторам."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff