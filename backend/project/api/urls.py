from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    UsersViewSet, TegViewSet, RecipeViewSet, IngredientViewSet, download_shopping_list)
from djoser.views import UserViewSet


router = DefaultRouter()
router.register(
    r'users', UsersViewSet, basename='users')
router.register(r'tags', TegViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

# http://localhost/api/recipes/download_shopping_cart/

urlpatterns = [
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'})),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('shopping_cart/download/', download_shopping_list, name='download_shopping_list'),
]
