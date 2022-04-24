import django_filters

from utils.filters import BaseFilterSet

from .models import Board, Stage, Tag, Task


class BoardFilterSet(BaseFilterSet):
    class Meta:
        model = Board
        fields = ["archived"]


class TaskFilters(BaseFilterSet):
    status = django_filters.CharFilter(
        field_name="stage__name", lookup_expr="icontains"
    )
    public = django_filters.BooleanFilter(field_name="board__public")

    class Meta:
        model = Task
        fields = ["archived", "public", "stage", "status"]
