from django.contrib import admin
from reviews.models import (
    ShoppingCart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_count', 'created_at')
    search_fields = ('author', 'name')
    list_filter = ('tags',)

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


admin.site.register(ShoppingCart, admin.ModelAdmin)
admin.site.register(Tag, admin.ModelAdmin)
admin.site.register(Favorite, admin.ModelAdmin)

admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
