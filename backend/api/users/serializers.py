from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from drf_extra_fields.fields import Base64ImageField

from project.settings import MAX_LENGT_EMAIL, MAX_LENGT_USERNAME
from users.models import Follow
from reviews.models import Recipe
from api.validators import validate_username
from api.serializers import RecipeShortSerializer


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
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
        serializer = RegistrationSerializer(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegistrationSerializer(serializers.ModelSerializer):
    """Вывод после регистрации"""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name')


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
    recipes_count = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        return Follow.objects.filter(
            user=current_user, following=obj.following).exists()

    def get_recipes(self, obj):
        """Метод для получения рецептов подписанного пользователя"""
        recipes = Recipe.objects.filter(author=obj.following)
        return RecipeShortSerializer(
            recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Общее количество рецептов пользователя"""
        return Recipe.objects.filter(author=obj.following).count()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.following.avatar:
            return request.build_absolute_uri(obj.following.avatar)
        return None
