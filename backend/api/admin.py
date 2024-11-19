from django.contrib import admin
from .models import (
    UserProfile, Recipe, Teg, Ingredient, Follow, Favorite,
    RecipeIngredient, Basket
)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username',)
    search_fields = ('email', 'username')
    list_display_links = ('username',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_count')
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


admin.site.register(Basket, admin.ModelAdmin)
admin.site.register(Teg, admin.ModelAdmin)
admin.site.register(Follow, admin.ModelAdmin)
admin.site.register(Favorite, admin.ModelAdmin)

admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
