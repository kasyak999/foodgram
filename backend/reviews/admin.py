from django.contrib import admin
from reviews.models import (
    ShoppingCart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
)
from django.db.models import Count
# from django.utils.html import format_html, mark_safe
from django.utils.safestring import mark_safe


class RecipeIngredientInline(admin.TabularInline):
    """Ингриенты в рецептах"""
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'formatted_cooking_time', 'author', 'tags_list',
        'favorites_count', 'image_preview')
    search_fields = ('tags__name', 'name')
    list_filter = ('author', 'tags',)
    inlines = [RecipeIngredientInline]

    @admin.display(description='Время приготовления')
    def formatted_cooking_time(self, obj):
        return f"{obj.cooking_time} мин"

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorites_count

    # @admin.display(description='Ингредиенты')
    # def formatted_ingredients(self, obj):
    #     """Отобразить ингредиенты с количеством как HTML"""
    #     ingredients_html = ''.join(
    #         f'<p>{ri.ingredient.name}: {ri.amount} {
    # ri.ingredient.measurement_unit}</p>'
    #         for ri in obj.recipeingredients.all()
    #     )
    #     return mark_safe(ingredients_html)

    @admin.display(description='Картинка')
    def image_preview(self, obj):
        """Показывать миниатюру изображения"""
        print(obj.image.url)
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" alt="Image" '
                f'style="max-height: 100px; max-width: 100px;"/>'
            )
        return 'Нет изображения'

    def get_queryset(self, request):
        result = super().get_queryset(request)
        return result.annotate(
            favorites_count=Count('favorites')).prefetch_related('tags')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
