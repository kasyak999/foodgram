from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from project.settings import MAX_LENGT_EMAIL, MAX_LENGT_USERNAME
from users.models import Follow
from .validators import validate_username


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
        if request.user.follower.filter(following=obj):
            return True
        return False


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""
    email = serializers.EmailField(
        max_length=MAX_LENGT_EMAIL,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Этот email уже используется")]
    )
    username = serializers.CharField(
        max_length=MAX_LENGT_USERNAME,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Этот username уже используется"), validate_username]
    )
    first_name = serializers.CharField(
        required=True, max_length=MAX_LENGT_USERNAME)
    last_name = serializers.CharField(
        required=True, max_length=MAX_LENGT_USERNAME)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')

    def to_representation(self, instance):
        serializer = RegistrationSerializer(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegistrationSerializer(serializers.ModelSerializer):
    """Вывод после регистрации"""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name')


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {'avatar': 'Является обязательным полем.'}
            )
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Подписчики"""
    email = serializers.EmailField(source='following.email', read_only=True)
    id = serializers.IntegerField(source='following.id', read_only=True)
    username = serializers.CharField(
        source='following.username', read_only=True)
    first_name = serializers.CharField(
        source='following.first_name', read_only=True)
    last_name = serializers.CharField(
        source='following.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return data

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if obj.following.following.filter(user=current_user):
            return True
        return False

    def get_recipes(self, obj):
        """Метод для получения рецептов подписанного пользователя"""
        from api.reviews.serializers import RecipeShortSerializer
        recipes = obj.following.recipes.all()
        return RecipeShortSerializer(
            recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Общее количество рецептов пользователя"""
        return obj.following.recipes.all().count()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.following.avatar:
            return request.build_absolute_uri(obj.following.avatar)
        return None
