from rest_framework import serializers

from .models import AccessLevel, Board, BoardAccess, Stage, Tag, Task, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "last_login",
            "date_joined",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "last_login", "date_joined")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "last_login")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "description", "modified_at", "created_at")


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color")


class TaskSerializer(serializers.ModelSerializer):

    tags = TagListSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "body",
            "priority",
            "archived",
            "tags",
            "stage",
            "modified_at",
            "created_at",
        )


class TaskListSerializer(serializers.ModelSerializer):

    tags = TagListSerializer(many=True)

    class Meta:
        model = Task
        fields = ("id", "name", "description", "tags", "priority")


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "archived",
            "board",
            "modified_at",
            "created_at",
        )


class StageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ("id", "name", "priority")


class BoardAccessSerializer(serializers.ModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = BoardAccess
        fields = (
            "id",
            "user",
            "board",
            "level",
            "modified_at",
            "created_at",
        )


class BoardSerializer(serializers.ModelSerializer):

    access_level = serializers.SerializerMethodField()
    # stages = StageSerializer(many=True, read_only=True)

    def get_access_level(self, obj) -> int:
        try:
            return BoardAccess.objects.get(
                user=self.context["request"].user, board=obj
            ).level
        except BoardAccess.DoesNotExist:
            return AccessLevel.NONE

    def create(self, validated_data):
        board = super().create(validated_data)
        # create owner level access for the user
        BoardAccess.objects.create(
            user=self.context["request"].user,
            board=board,
            level=AccessLevel.OWNER,
        )
        return board

    class Meta:
        model = Board
        fields = (
            "id",
            "name",
            "description",
            "archived",
            "modified_at",
            "created_at",
            "access_level",
            # "stages",
        )


class BoardListSerializer(serializers.ModelSerializer):

    access_level = serializers.SerializerMethodField()

    def get_access_level(self, obj) -> int:
        return BoardAccess.objects.get(
            user=self.context["request"].user, board=obj
        ).level

    class Meta:
        model = Board
        fields = (
            "id",
            "name",
            "description",
            "archived",
            "modified_at",
            "created_at",
            "access_level",
        )
