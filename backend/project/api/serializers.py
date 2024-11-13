from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken
from .models import (
    MAX_LENGT_EMAIL, MAX_LENGT_USERNAME, Teg, Recipe, Ingredient, Follow)
from .validators import validate_username


import base64
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.core.exceptions import ValidationError

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
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsersSerializer(UserRegistrationSerializer):
    """Сериализатор для /me и пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'avatar',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        return Follow.objects.filter(user=current_user, following=obj).exists()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""
    avatar = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['avatar']

    def validate_avatar(self, value):
        """Проверка валидности данных аватара (base64)"""
        try:
            format, imgstr = value.split(';base64,')
            ext = format.split('/')[1]  # Получаем расширение файла
            imgdata = base64.b64decode(imgstr)  # Декодируем base64 в байты

            # Сохраняем изображение в виде файла
            Image.open(BytesIO(imgdata))
            file_name = f"avatar.{ext}"
            content_file = ContentFile(imgdata, name=file_name)
            return content_file
        except (ValueError, TypeError, ValidationError):
            raise serializers.ValidationError("Некорректный формат изображения.")


class TegSerializer(serializers.ModelSerializer):
    """Серелизатор для вывода тегов"""
    class Meta:
        model = Teg
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Серелизатор для вывода ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Серелизатор для рецептов"""
    tags = serializers.SerializerMethodField(read_only=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TegSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time']


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


class RecipeShortSerializer(serializers.ModelSerializer):
    """Свернутый сериализатор для рецептов"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
