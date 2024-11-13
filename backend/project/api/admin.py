from django.contrib import admin
from .models import (
    UserProfile, Recipe, Teg, Ingredient, Follow
)


admin.site.register(Recipe, admin.ModelAdmin)
admin.site.register(Teg, admin.ModelAdmin)
admin.site.register(Ingredient, admin.ModelAdmin)
admin.site.register(UserProfile, admin.ModelAdmin)
admin.site.register(Follow, admin.ModelAdmin)
