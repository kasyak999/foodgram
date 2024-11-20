from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    UsersViewSet, TagViewSet, RecipeViewSet, IngredientViewSet)
from djoser.views import UserViewSet


router = DefaultRouter()
router.register(
    r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'})),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
