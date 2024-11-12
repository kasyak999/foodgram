from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken
from .models import MAX_LENGT_EMAIL, MAX_LENGT_USERNAME
from .validators import validate_username


import base64
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.core.exceptions import ValidationError

User = get_user_model()


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
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsersSerializer(UserRegistrationSerializer):
    """Сериализатор для /me и пользователей"""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name')


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""
    avatar = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['avatar']

    def validate_avatar(self, value):
        """Проверка валидности данных аватара (base64)"""
        try:
            format, imgstr = value.split(';base64,')
            ext = format.split('/')[1]  # Получаем расширение файла
            imgdata = base64.b64decode(imgstr)  # Декодируем base64 в байты

            # Сохраняем изображение в виде файла
            Image.open(BytesIO(imgdata))
            file_name = f"avatar.{ext}"
            content_file = ContentFile(imgdata, name=file_name)
            return content_file
        except (ValueError, TypeError, ValidationError):
            raise serializers.ValidationError("Некорректный формат изображения.")