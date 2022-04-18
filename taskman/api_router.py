from django.conf import settings
from rest_framework_nested import routers

from .api_views import (
    BoardAccessViewSet,
    BoardViewSet,
    StageViewSet,
    TagViewSet,
    TaskViewSet,
    UserViewSet,
)

app_name = "api"

router = routers.SimpleRouter(trailing_slash=False)
NestedRouter = routers.NestedSimpleRouter
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)
    NestedRouter = routers.NestedDefaultRouter

router.register(r"users", UserViewSet)
router.register(r"boards", BoardViewSet)
router.register(r"tasks", TaskViewSet)

boards_router = NestedRouter(router, r"boards", lookup="board")
boards_router.register(r"access", BoardAccessViewSet)
boards_router.register(r"stages", StageViewSet)
boards_router.register(r"tags", TagViewSet)
boards_router.register(r"tasks", TaskViewSet)

stages_router = NestedRouter(boards_router, r"stages", lookup="stage")
stages_router.register(r"tasks", TaskViewSet)


urlpatterns = router.urls + boards_router.urls + stages_router.urls
