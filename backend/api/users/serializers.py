from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from project.settings import MAX_LENGT_EMAIL, MAX_LENGT_USERNAME
from users.models import Follow
from .validators import validate_username


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для /me и пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.follower.filter(following=obj).exists()


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""
    email = serializers.EmailField(
        max_length=MAX_LENGT_EMAIL,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Этот email уже используется")]
    )
    username = serializers.CharField(
        max_length=MAX_LENGT_USERNAME,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Этот username уже используется"), validate_username]
    )
    first_name = serializers.CharField(
        required=True, max_length=MAX_LENGT_USERNAME)
    last_name = serializers.CharField(
        required=True, max_length=MAX_LENGT_USERNAME)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result.pop('password')
        return result

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {'avatar': 'Является обязательным полем.'}
            )
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Подписчики"""
    email = serializers.EmailField(source='following.email', read_only=True)
    id = serializers.IntegerField(source='following.id', read_only=True)
    username = serializers.CharField(
        source='following.username', read_only=True)
    first_name = serializers.CharField(
        source='following.first_name', read_only=True)
    last_name = serializers.CharField(
        source='following.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        return True if obj.following else False

    def get_recipes(self, obj):
        """Метод для получения рецептов подписанного пользователя"""
        from api.reviews.serializers import RecipeShortSerializer
        recipes = obj.following.recipes.all()
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_avatar(self, obj):
        if obj.following.avatar:
            return obj.following.avatar.url
        return None


class AddFollowSerializer(serializers.ModelSerializer):
    """Добавление подписчиков"""
    class Meta:
        model = None
        fields = 'following', 'user'

    def __init__(self, *args, **kwargs):
        self.Meta.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return data

    def to_representation(self, instance):
        instance.recipes_count = instance.following.recipes.count()
        serializer = FollowSerializer(instance, context=self.context)
        return serializer.data
