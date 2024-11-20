from django.contrib import admin
from users.models import UserProfile
from .models import Follow


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username',)
    search_fields = ('email', 'username')
    list_display_links = ('username',)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Follow, admin.ModelAdmin)