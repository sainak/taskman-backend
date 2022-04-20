from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from .mixins import GetSerializerClassMixin, PartialUpdateModelMixin


class BaseModelViewSet(
    GetSerializerClassMixin,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    PartialUpdateModelMixin,
    GenericViewSet,
):
    pass
