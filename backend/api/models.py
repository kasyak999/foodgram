import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


MAX_LENGT_EMAIL = 254
MAX_LENGT_USERNAME = 150
WEIGHT_UNITS = [
    ('кг', 'Килограмм'),
    ('г', 'Грамм'),
    ('мл', 'Милилитр'),
    ('шт.', 'Штук'),
    ('капля', 'капля'),
    ('л', 'Литр'),
    ('банка', 'банка'),
    ('стакан', 'стакан'),
    ('щепотка', 'щепотка'),
    ('ч. л.', 'Чайная ложка'),
    ('веточка', 'веточка'),
    ('батон', 'батон')
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
    tags = models.ManyToManyField('Tag', verbose_name='Теги')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления', help_text='в минутах')
    link = models.CharField(
        max_length=10, unique=True, blank=True, null=True,
        verbose_name='Ссылка')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )
    image = models.ImageField(upload_to='images/', verbose_name='Картинка')
    text = models.TextField(verbose_name='Текстовое описание')

    def generate_link(self):
        if not self.link:
            self.link = uuid.uuid4().hex[:3]

    class Meta:
        """Перевод модели"""
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-created_at',)


class Tag(PublishedModel):
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
    measurement_unit = models.CharField(
        max_length=10, choices=WEIGHT_UNITS, default='кг',
        verbose_name='Единица измерения')

    class Meta:
        """Перевод модели"""
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class RecipeIngredient(models.Model):
    """Количество ингредиентов"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', blank=False)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        """Перевод модели"""
        verbose_name = 'количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name}'


class Follow(models.Model):
    """Подписки пользователей"""
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='на кого подписан')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик')

    class Meta:
        """Перевод модели"""
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_name_owner'
            )
        ]

    def __str__(self):
        return f'Подписчик {self.user}'


class Favorite(models.Model):
    """Избраные рецепты"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Подписчик')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепты')

    class Meta:
        """Перевод модели"""
        verbose_name = 'избраное'
        verbose_name_plural = 'Избраное'
        default_related_name = 'favorites'

    def __str__(self):
        return f'Подписчик {self.user}'


class ShoppingCart(models.Model):
    """Список покупок или корзина"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_shopping_cart',
        verbose_name='Рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart')
        ]
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user.username} — {self.recipe.name}'
