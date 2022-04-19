from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.models.base import BaseModel

from .validators import avatar_validator


class AccessLevel(models.IntegerChoices):
    OWNER = 0
    ADMIN = 100
    READ_WRITE = 1000
    READ_ONLY = 2000


class User(AbstractUser):
    avatar = models.CharField(
        max_length=2048, blank=True, null=True, validators=[avatar_validator]
    )

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = f"https://avatars.dicebear.com/api/identicon/{self.email}.svg"
        super().save(*args, **kwargs)


class Board(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    archived = models.BooleanField(default=False, db_index=True)

    access = models.ManyToManyField(
        User,
        through="BoardAccess",
        through_fields=("board", "user"),
        related_name="boards",
    )

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"

    def get_access_level(self, user_id):
        try:
            access = self.access.through.objects.get(board_id=self.id, user_id=user_id)
        except BoardAccess.DoesNotExist:
            return None
        return access.level


class BoardAccess(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    level = models.PositiveIntegerField(
        choices=AccessLevel.choices, default=AccessLevel.READ_WRITE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["board", "user"], name="unique_board_access"
            )
        ]

    def __str__(self) -> str:
        return f"user:{self.user.id} - board:{self.board.id}:{self.level}"


class Tag(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=8, blank=True)

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tags")

    def __str__(self) -> str:
        return f"user:{self.owner.id} - {self.id}:{self.name}"

    def get_access_level(self, user_id):
        try:
            access = self.board.access.through.objects.get(
                board_id=self.id, user_id=user_id
            )
        except BoardAccess.DoesNotExist:
            return None
        return access.level

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_tag_name_per_board",
                fields=["board", "name"],
                condition=models.Q(deleted=False),
            )
        ]


class Stage(SortableMixin, BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    archived = models.BooleanField(default=False, db_index=True)
    priority = models.PositiveIntegerField(default=0, db_index=True)

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="stages")

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"

    def get_access_level(self, user_id):
        try:
            access = self.board.access.through.objects.get(
                board_id=self.id, user_id=user_id
            )
        except BoardAccess.DoesNotExist:
            return None
        return access.level

    class Meta:
        ordering = ["priority"]


class Task(SortableMixin, BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    body = models.TextField(blank=True)
    archived = models.BooleanField(default=False, db_index=True)
    priority = models.PositiveIntegerField(default=0, db_index=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    stage = SortableForeignKey(Stage, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"

    def get_access_level(self, user_id):
        try:
            access = self.stage.board.access.through.objects.get(
                board_id=self.id, user_id=user_id
            )
        except BoardAccess.DoesNotExist:
            return None
        return access.level
