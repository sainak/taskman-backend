from rest_framework import permissions

from .models import AccessLevel


class IsSelfOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class BoardAccessPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, _, obj):
        access = obj.get_access_level(request.user.id)

        if access is None:
            return False

        return (
            access <= AccessLevel.READ_ONLY
            if request.method in permissions.SAFE_METHODS
            else access <= AccessLevel.READ_WRITE
        )
