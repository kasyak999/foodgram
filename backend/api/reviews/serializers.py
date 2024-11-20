from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from reviews.models import (
    Tag, Recipe, Ingredient, Favorite, RecipeIngredient, ShoppingCart)
from ..users.serializers import UsersSerializer


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


class AddRecipeIngredientSerializer(serializers.Serializer):
    """Сериализатор для добавления ингредиента и количества"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


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
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        result = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(result, many=True).data


class AddRecipeSerializer(serializers.ModelSerializer):
    """Серелизатор для добавления рецептов"""
    ingredients = AddRecipeIngredientSerializer(
        many=True, min_length=1, error_messages={
            "min_length": "Список ингредиентов не должен быть пустым."
        })
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'name',
            'cooking_time', 'link']

    def validate(self, attrs):
        if 'ingredients' not in attrs:
            raise serializers.ValidationError({
                "ingredients": "Поле 'ingredients' является обязательным."
            })
        return attrs

    def validate_ingredients(self, value):
        # if len(value) < 2:
        #     raise ValidationError("Не может быть только один игридиент")
        for ingredient in value:
            if not Ingredient.objects.filter(id=ingredient['id']):
                raise serializers.ValidationError("Ингредиент с таким ID не существует.")
        ingredient_list = []
        for ingredient in value:
            if ingredient['id'] in ingredient_list:
                raise serializers.ValidationError("Не может быть одинаковых игридиентов")
            ingredient_list.append(ingredient['id'])
        return value

    def to_representation(self, instance):
        recipe_serializer = RecipeSerializer(instance, context=self.context)
        return recipe_serializer.data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        recipe = super().create(validated_data)

        if not recipe.link:
            recipe.generate_link()
            recipe.save()
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags_data:
            instance.tags.set(tags_data)
        instance.recipeingredient_set.all().delete()
        for ingredient in ingredients_data:
            ingredient_instance = Ingredient.objects.get(id=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_instance,
                amount=ingredient['amount']
            )
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Свернутый сериализатор для рецептов"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
