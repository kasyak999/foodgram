from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from reviews.models import (
    Tag, Recipe, Ingredient, Favorite, RecipeIngredient, ShoppingCart)
from api.users.serializers import UsersSerializer
from api.utils import recipe_create_and_update


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Серелизатор для вывода тегов"""
    class Meta:
        model = Tag
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


#  -------------------------------------------------------

class RecipeSerializer(serializers.ModelSerializer):
    """Серелизатор для списка рецептов"""
    author = UsersSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        result = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(result, many=True).data


class AddRecipeIngredientSerializer(serializers.Serializer):
    """Сериализатор для добавления ингредиента и количества"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class AddRecipeSerializer(serializers.ModelSerializer):
    """Серелизатор для добавления рецептов"""
    ingredients = AddRecipeIngredientSerializer(
        many=True, min_length=2, error_messages={
            "min_length":
            "Список ингредиентов не должен быть пустым или быть больше 1."
        })
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'name',
            'cooking_time', 'link']

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                "Не может быть пустым.")
        return value

    def validate_ingredients(self, value):
        ingredient_set = {ingredient['id'] for ingredient in value}
        if len(value) > len(ingredient_set):
            raise serializers.ValidationError(
                "Не может быть одинаковых игридиентов")
        return value

    def to_representation(self, instance):
        recipe_serializer = RecipeSerializer(instance, context=self.context)
        return recipe_serializer.data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        recipe = super().create(validated_data)
        recipe_create_and_update(recipe, ingredients_data, tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        recipe = super().update(instance, validated_data)
        recipe_create_and_update(recipe, ingredients_data, tags_data)
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Свернутый сериализатор для рецептов"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class AddFavoriteSerializer(serializers.ModelSerializer):
    """Добавление в избраное"""
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(instance.recipe)
        return serializer.data


class AddShoppingCartSerializer(serializers.ModelSerializer):
    """Добавление в избраное"""
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(instance.recipe)
        return serializer.data
