from rest_framework import permissions

from .models import AccessLevel


class IsSelfOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class BoardAccessPermission(permissions.IsAuthenticated):
    def __init__(
        self,
        read_level=AccessLevel.READ_ONLY,
        write_level=AccessLevel.READ_WRITE,
    ):
        super().__init__()
        self.read_level = read_level
        self.write_level = write_level

    def has_object_permission(self, request, _, obj):
        access = obj.get_access_level(request.user.id)

        if access is None:
            return False

        return (
            access <= self.read_level
            if request.method in permissions.SAFE_METHODS
            else access <= self.write_level
        )
