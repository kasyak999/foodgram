from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken
from .models import (
    MAX_LENGT_EMAIL, MAX_LENGT_USERNAME, Teg, Recipe, Ingredient, Follow,
    Favorite, RecipeIngredient)
from .validators import validate_username, checking_avatar


import base64
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from pprint import pprint

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
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""
    avatar = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['avatar']

    def validate_avatar(self, value):
        return checking_avatar(value)


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов и количества"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Серелизатор для списка рецептов"""
    author = UsersSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TegSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited', 'name',
            'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        result = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(result, many=True).data


# class IngredientAmountSerializer(serializers.Serializer):
#     """Сериализатор для указания ингредиента и его количества"""
#     id = serializers.IntegerField()
#     amount = serializers.IntegerField()


class AddRecipeSerializer(serializers.ModelSerializer):
    """Серелизатор для добавления рецептов"""
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'name',
            'cooking_time']

    def to_representation(self, instance):
        recipe_serializer = RecipeSerializer(instance, context=self.context)
        return recipe_serializer.data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe.ingredients.add(
                ingredient, through_defaults={
                    'amount': ingredient_data['amount']})
        return recipe

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            instance.name = validated_data['name']
        if 'text' in validated_data:
            instance.text = validated_data['text']
        if 'cooking_time' in validated_data:
            instance.cooking_time = validated_data['cooking_time']
        if 'image' in validated_data:
            instance.image = validated_data['image']

        if 'tags' in validated_data:
            tags_data = validated_data['tags']
            instance.tags.set(tags_data)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data['ingredients']
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get(id=ingredient_data['id'])
                instance.ingredients.add(
                    ingredient, through_defaults={
                        'amount': ingredient_data['amount']}
                )

        return instance


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