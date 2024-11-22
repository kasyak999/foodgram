from django.contrib import admin
from .models import Follow
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe


User = get_user_model()


@admin.register(User)
class UserProfileAdmin(UserAdmin):
    list_display = ('pk', 'username', 'image_preview')
    search_fields = ('email', 'username')
    list_display_links = ('username',)

    @admin.display(description='Аватар')
    def image_preview(self, obj):
        """Показывать миниатюру изображения"""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" alt="Image" '
                f'style="max-height: 100px; max-width: 100px;"/>'
            )
        return 'Нет изображения'

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following',)
