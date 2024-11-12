from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


MAX_LENGT_EMAIL = 254
MAX_LENGT_USERNAME = 150
WEIGHT_UNITS = [
    ('kg', 'Килограммы'),
    ('g', 'Граммы'),
]


class UserProfile(AbstractUser):
    email = models.EmailField(
        unique=True, blank=True, max_length=MAX_LENGT_EMAIL)
    username = models.CharField(
        max_length=MAX_LENGT_USERNAME, blank=True, unique=True)
    avatar = models.ImageField(upload_to='users/', null=True, blank=True)

    class Meta:
        """Перевод модели"""

        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


User = get_user_model()


class PublishedModel(models.Model):
    """Базовая модель"""

    name = models.CharField(
        verbose_name='Название', max_length=MAX_LENGT_USERNAME, unique=True)

    class Meta:
        abstract = True
        ordering = ('created_at',)

    def __str__(self):
        return self.name


class Recipe(PublishedModel):
    """Рецепт"""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    picture = models.ImageField(upload_to='images/', verbose_name='Картинка')
    description = models.TextField(verbose_name='Текстовое описание')
    Ingredient = models.ManyToManyField(
        'Ingredient', verbose_name='Ингредиенты')
    tag = models.ManyToManyField('Teg', verbose_name='Теги')
    time_preparations = models.IntegerField(
        verbose_name='Время приготовления', help_text='в минутах')

    class Meta:
        """Перевод модели"""
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'


class Teg(PublishedModel):
    """Тег"""

    slug = models.SlugField(
        unique=True,
        help_text=(
            "Slug страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        )
    )

    class Meta:
        """Перевод модели"""
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(PublishedModel):
    """Ингредиент"""
    quantity = models.IntegerField(verbose_name='Количество')
    weight_unit = models.CharField(
        max_length=2, choices=WEIGHT_UNITS, default='g',
        verbose_name='Единица измерения')

    class Meta:
        """Перевод модели"""
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
