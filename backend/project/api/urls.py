from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet
from djoser.views import UserViewSet


router = DefaultRouter()
router.register(
    r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'})),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
