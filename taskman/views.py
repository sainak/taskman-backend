from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from utils.views.base import BaseModelViewSet
from utils.views.mixins import PartialUpdateModelMixin

from .models import Board, BoardAccess, Stage, Tag, Task, User
from .permissions import BoardAccessPermission, IsSelfOrReadOnly
from .serializers import (
    BoardAccessSerializer,
    BoardListSerializer,
    BoardSerializer,
    StageListSerializer,
    StageSerializer,
    TagListSerializer,
    TagSerializer,
    TaskListSerializer,
    TaskSerializer,
    UserSerializer,
)


class BaseApiViewSet(BaseModelViewSet):
    permission_classes = (BoardAccessPermission,)


@extend_schema_view(
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
)
class UserViewSet(
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    PartialUpdateModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return (permissions.AllowAny(),)
        return (IsSelfOrReadOnly(),)

    def get_object(self):
        return (
            super().get_object()
            if self.kwargs.get(self.lookup_field)
            else self.request.user
        )

    @action(detail=False)
    def me(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @me.mapping.delete
    def destroy_me(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BoardViewSet(BaseApiViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.filter(access__id=self.request.user.id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return BoardListSerializer
        return super().get_serializer_class()


class BoardAccessViewSet(BaseApiViewSet):
    queryset = BoardAccess.objects.all()
    serializer_class = BoardAccessSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board=board_pk)
        if self.action == "list":
            return qs.filter(access__id=self.request.user.id)
        return qs


class StageViewSet(BaseApiViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board=board_pk)
        if self.action == "list":
            return qs.filter(board__access__id=self.request.user.id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return StageListSerializer
        return super().get_serializer_class()


class TagViewSet(BaseApiViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board__id=board_pk)
        if self.action == "list":
            return qs.filter(board__access__id=self.request.user.id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return TagListSerializer
        return super().get_serializer_class()


class TaskViewSet(BaseApiViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board=board_pk)
        if stage_pk := self.kwargs.get("stage_pk"):
            qs.filter(stage=stage_pk)
        if self.action == "list":
            return qs.filter(board__access__id=self.request.user.id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        return super().get_serializer_class()
