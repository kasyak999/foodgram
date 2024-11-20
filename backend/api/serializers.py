from rest_framework import serializers
from reviews.models import Recipe
from users.models import Follow
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для /me и пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Свернутый сериализатор для рецептов"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
