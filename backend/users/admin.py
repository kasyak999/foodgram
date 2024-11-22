from django.contrib import admin
from .models import Follow
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username',)
    search_fields = ('email', 'username')
    list_display_links = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following',)
