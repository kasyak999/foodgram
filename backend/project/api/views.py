from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from .serializers import (
    UserRegistrationSerializer, UsersSerializer, UserAvatarSerializer,
    TegSerializer, RecipeSerializer, IngredientSerializer, FollowSerializer,
    RecipeShortSerializer, AddRecipeSerializer)
from rest_framework.pagination import LimitOffsetPagination
from .models import Teg, Recipe, Ingredient, Follow, Favorite
from django.shortcuts import get_object_or_404

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
        detail=False, methods=['put', 'delete'], url_path='me/avatar',
        permission_classes=[IsAuthenticated])
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
                    {'avatar': user.avatar.url})
            return Response(serializer.errors, status=400)
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(
                {"detail": "Аватар успешно удален"},
                status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], url_path='subscriptions')
    def user_Follow(self, request):
        """Список подписок"""
        follows = Follow.objects.filter(user=request.user)
        paginator = LimitOffsetPagination()
        paginated_follows = paginator.paginate_queryset(follows, request)
        serializer = FollowSerializer(
            paginated_follows, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Подписаться или отписаться от пользователя"""
        result = get_object_or_404(User, pk=pk)
        follow = Follow.objects.filter(user=request.user, following=result)
        if request.method == 'POST':
            if result == request.user or follow.exists():
                return Response(
                    {"detail": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=request.user, following=result)
            serializer = FollowSerializer(follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if follow.exists():
                follow.delete()
                return Response(
                    {"detail": "Вы успешно отписались от пользователя."},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )


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
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return AddRecipeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление и удаление из избраного"""
        result = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(user=request.user, recipe=result)
        if request.method == 'POST':
            if favorite.exists():
                return Response(
                    {"detail": "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=result)
            serializer = RecipeShortSerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response(
                    {"detail": "Рецепт успешно удален из избранного."},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {"detail": "Рецепт отсутствует в избранном."},
                status=status.HTTP_400_BAD_REQUEST
            )
