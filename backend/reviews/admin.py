from django.contrib import admin
from reviews.models import (
    ShoppingCart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
)
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter


class CookingTimeFilter(SimpleListFilter):
    """Фильтр для времени готовки."""
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        """Определяем параметры фильтра."""
        return [
            ('less_than_10', 'быстрее 10 мин'),
            ('less_than_60', 'быстрее 60 мин'),
            ('long', 'долго'),
        ]

    def queryset(self, request, queryset):
        """Фильтруем данные в зависимости от выбранного параметра."""
        value = self.value()
        if value == 'less_than_10':
            return queryset.filter(cooking_time__lt=10)
        if value == 'less_than_60':
            return queryset.filter(cooking_time__lt=60)
        if value == 'long':
            return queryset.filter(cooking_time__gte=60)
        return queryset


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
    list_filter = ('author', 'tags', CookingTimeFilter)
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

    @admin.display(description='Картинка')
    def image_preview(self, obj):
        """Показывать миниатюру изображения"""
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
