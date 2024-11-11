from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserVerificationViewSet, UserRegistrationViewSet

router = DefaultRouter()
# router.register(r'auth/token', UserVerificationViewSet, basename='token')
router.register(
    r'users', UserRegistrationViewSet, basename='registration')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', UserVerificationViewSet.as_view(), name='token'),
]