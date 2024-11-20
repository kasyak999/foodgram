from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, AllowAny)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from users.models import Follow
from api.serializers import UsersSerializer
from .serializers import (
    UserRegistrationSerializer, UserAvatarSerializer, FollowSerializer,
)


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
        detail=False, methods=['get'], url_path='me',
        permission_classes=[IsAuthenticated])
    def user_information(self, request):
        """users/me"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['put'], url_path='me/avatar',
        permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Добавить аватар пользователя"""
        user = request.user
        serializer = UserAvatarSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            user.avatar = serializer.validated_data.get('avatar')
            user.save()
            return Response(
                {'avatar': user.avatar.url})
        return Response(serializer.errors, status=400)

    @avatar.mapping.delete
    def avatar_delete(self, request):
        """Удалить аватар пользователя"""
        user = request.user
        user.avatar.delete()
        return Response(
            {"detail": "Аватар успешно удален"},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        permission_classes=[IsAuthenticated])
    def user_Follow(self, request):
        """Список подписок"""
        follows = Follow.objects.filter(user=request.user)
        paginator = LimitOffsetPagination()
        paginated_follows = paginator.paginate_queryset(follows, request)
        serializer = FollowSerializer(
            paginated_follows, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post'], url_path='subscribe',
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя"""
        result = get_object_or_404(User, pk=pk)
        follow = Follow.objects.filter(user=request.user, following=result)
        if result == request.user or follow.exists():
            return Response(
                {"detail": "Вы уже подписанны"},
                status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.create(user=request.user, following=result)
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        """Отписаться от пользователя"""
        result = get_object_or_404(User, pk=pk)
        follow = Follow.objects.filter(user=request.user, following=result)
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