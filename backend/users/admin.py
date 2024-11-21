from django.contrib import admin
from .models import Follow
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model


User = get_user_model()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username',)
    search_fields = ('email', 'username')
    list_display_links = ('username',)


admin.site.register(User, UserProfileAdmin)
admin.site.register(Follow, admin.ModelAdmin)
