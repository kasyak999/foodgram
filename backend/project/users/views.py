from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, filters, viewsets, mixins
from rest_framework.decorators import action
# from api.permissions import IsAdmin
from .serializers import TokenSerializer, UserRegistrationSerializer
# from .utils import send_verification_email, generate_verification_code

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


User = get_user_model()


class UserRegistrationViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """Регистрация пользователя"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserVerificationViewSet(APIView):
    """Верификация пользователя и получение токена."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
