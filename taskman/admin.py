from adminsortable.admin import (
    NonSortableParentAdmin,
    SortableAdmin,
    SortableTabularInline,
)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin

from .models import Board, BoardAccess, Stage, Tag, Task, User


class BaseAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(DjangoQLSearchMixin, BaseUserAdmin):
    pass


@admin.register(BoardAccess)
class BoardAccessAdmin(BaseAdmin):
    pass


@admin.register(Board)
class BoardAdmin(BaseAdmin):
    pass


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    pass


@admin.register(Stage)
class StageAdmin(SortableAdmin, BaseAdmin):
    pass


@admin.register(Task)
class TaskAdmin(SortableAdmin, BaseAdmin):
    pass
