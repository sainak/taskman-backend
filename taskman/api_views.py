from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import permissions, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.views.base import BaseModelViewSet

from .filters import TaskFilters
from .models import AccessLevel, Board, BoardAccess, Stage, Tag, Task, User
from .permissions import BoardAccessPermission, IsSelfOrReadOnly
from .serializers import (
    AuthSerializer,
    BoardDetailAccessSerializer,
    BoardDetailSerializer,
    BoardSerializer,
    FullBoardSerializer,
    HomeDetailSerializer,
    StageDetailSerializer,
    StageSerializer,
    TagDetailSerializer,
    TagSerializer,
    TaskDetailSerializer,
    TaskSerializer,
    UserDetailSerializer,
)


class BaseApiViewSet(BaseModelViewSet):
    permission_classes = (BoardAccessPermission,)


class AuthViewSet(GenericViewSet):
    def get_permissions(self):
        if self.action == "login":
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def get_serializer_class(self):
        if self.action == "login":
            return AuthSerializer
        return super().get_serializer_class()

    @extend_schema(
        tags=("auth",),
        operation_id="api-login",
        responses={
            200: inline_serializer(
                "TokenSerializer",
                {
                    "token": serializers.CharField(),
                },
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

    @extend_schema(
        tags=("auth",),
        operation_id="api-logout",
    )
    @action(detail=False, methods=["delete"])
    def logout(self, request: Request):
        if auth_token := request.auth:
            Token.objects.filter(key=auth_token).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ParseError("No auth token provided")


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    list=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

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

    def list(self, request, *args, **kwargs):
        raise NotFound

    @action(detail=False)
    def me(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @me.mapping.delete
    def destroy_me(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BoardViewSet(BaseModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    serializer_action_classes = {
        "retrieve": FullBoardSerializer,
        "list": BoardSerializer,
    }

    def get_permissions(self):
        return (BoardAccessPermission(AccessLevel.READ_ONLY, AccessLevel.ADMIN),)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.filter(Q(access__id=self.request.user.id) | Q(public=True))
        elif self.action == "retrieve":
            qs = qs.prefetch_related(
                "stages",
                "stages__tasks",
                "stages__tasks__tags",
            )
        return qs


class BoardAccessViewSet(BaseModelViewSet):
    queryset = BoardAccess.objects.all()
    serializer_class = BoardDetailAccessSerializer

    def get_permissions(self):
        return (BoardAccessPermission(AccessLevel.READ_ONLY, AccessLevel.OWNER),)

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs = qs.filter(board=board_pk)
        if self.action == "list":
            qs = qs.filter(access__id=self.request.user.id)
        return qs


class StageViewSet(BaseApiViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageDetailSerializer
    serializer_action_classes = {
        "list": StageSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs = qs.filter(board=board_pk)
        if self.action == "list":
            qs = qs.filter(board__access__id=self.request.user.id)
        elif self.action == "retrieve":
            qs = qs.prefetch_related(
                "tasks",
                "tasks__tags",
            )
        return qs


class TagViewSet(BaseApiViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    serializer_action_classes = {
        "list": TagSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board__id=board_pk)
        if self.action == "list":
            qs = qs.filter(
                Q(board__access__id=self.request.user.id) | Q(board__public=True)
            )
        return qs


class TaskViewSet(BaseApiViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    serializer_action_classes = {
        "list": TaskSerializer,
    }
    filterset_class = TaskFilters

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs = qs.filter(board=board_pk)
        if stage_pk := self.kwargs.get("stage_pk"):
            qs = qs.filter(stage=stage_pk)
        if self.action == "list":
            qs = qs.filter(
                Q(board__access__id=self.request.user.id) | Q(board__public=True)
            )
        elif self.action == "retrieve":
            qs = qs.prefetch_related(
                "tags",
            )
        return qs


class HomeViewSet(GenericViewSet):
    serializer_class = HomeDetailSerializer

    @action(detail=False, methods=["get"])
    def summary(self, request, *args, **kwargs):
        tasks = (
            Task.objects.filter(board__access__id=self.request.user.id)
            .filter(stage__name__in=["To Do", "In Progress", "Done"])
            .order_by("stage")
            .values("stage__name")
            .annotate(count=Count("stage__name"))
        )
        done = list(filter(lambda x: x["stage__name"] == "Done", tasks))
        in_progress = list(filter(lambda x: x["stage__name"] == "In Progress", tasks))
        to_do = list(filter(lambda x: x["stage__name"] == "To Do", tasks))
        return Response(
            {
                "done": done[0]["count"] if done else 0,
                "in_progress": in_progress[0]["count"] if in_progress else 0,
                "to_do": to_do[0]["count"] if to_do else 0,
            }
        )
