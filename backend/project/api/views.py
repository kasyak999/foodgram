from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from .serializers import (
    UserRegistrationSerializer, UsersSerializer, UserAvatarSerializer,
    TegSerializer, RecipeSerializer, IngredientSerializer, FollowSerializer)
from rest_framework.pagination import LimitOffsetPagination
from .models import Teg, Recipe, Ingredient, Follow

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Пользователи"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UsersSerializer

    @action(
        detail=False, methods=['get'], url_path='me')
    def user_information(self, request):
        """users/me"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        """Аватар пользователя"""
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                user.avatar = serializer.validated_data.get('avatar')
                user.save()
                return Response(
                    {'avatar': request.build_absolute_uri(user.avatar)})
            return Response(serializer.errors, status=400)
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(
                {"detail": "Аватар успешно удален"},
                status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], url_path='subscriptions')
    def user_Follow(self, request):
        """users/subscriptions"""
        follows = Follow.objects.filter(user=request.user)
        paginator = LimitOffsetPagination()
        paginated_follows = paginator.paginate_queryset(follows, request)
        serializer = FollowSerializer(
            paginated_follows, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class TegViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги"""
    queryset = Teg.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TegSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты"""
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):  # не готово
    """Рецепты"""
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
