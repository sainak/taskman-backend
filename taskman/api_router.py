from django.conf import settings
from rest_framework_nested import routers

from .views import (
    BoardAccessViewSet,
    BoardViewSet,
    StageViewSet,
    TagViewSet,
    TaskViewSet,
    UserViewSet,
)

app_name = "api"

router = (
    routers.DefaultRouter(trailing_slash=False)
    if settings.DEBUG
    else routers.SimpleRouter(trailing_slash=False)
)
router.register(r"users", UserViewSet)
router.register(r"boards", BoardViewSet)
router.register(r"tasks", TaskViewSet)

boards_router = routers.NestedSimpleRouter(
    router, r"boards", lookup="board", trailing_slash=False
)
boards_router.register(r"access", BoardAccessViewSet)
boards_router.register(r"stages", StageViewSet)
boards_router.register(r"tags", TagViewSet)
boards_router.register(r"tasks", TaskViewSet)

stages_router = routers.NestedSimpleRouter(
    boards_router, r"stages", lookup="stage", trailing_slash=False
)
stages_router.register(r"tasks", TaskViewSet)


urlpatterns = router.urls + boards_router.urls + stages_router.urls
