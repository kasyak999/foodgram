import uuid
from django.db import models
from django.contrib.auth import get_user_model
from project.settings import MAX_LENGT_USERNAME
# from django.core.exceptions import ValidationError


User = get_user_model()
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


class PublishedModel(models.Model):
    """Базовая модель"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        abstract = True
        ordering = ('user',)


class Tag(models.Model):
    """Тег"""
    name = models.CharField(
        verbose_name='Название', max_length=MAX_LENGT_USERNAME, unique=True)
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
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиент"""
    name = models.CharField(
        verbose_name='Название', max_length=MAX_LENGT_USERNAME)
    measurement_unit = models.CharField(
        max_length=10, choices=WEIGHT_UNITS, default='кг',
        verbose_name='Единица измерения')

    class Meta:
        """Перевод модели"""
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""
    name = models.CharField(
        verbose_name='Название', max_length=MAX_LENGT_USERNAME, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
    )
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

    def __str__(self):
        return self.name


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
        default_related_name = 'recipeingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name}'


class Favorite(PublishedModel):
    """Избраные рецепты"""

    class Meta(PublishedModel.Meta):
        """Перевод модели"""
        verbose_name = 'избраное'
        verbose_name_plural = 'Избраное'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_recipe')
        ]

    def __str__(self):
        return self.user


class ShoppingCart(PublishedModel):
    """Список покупок или корзина"""

    class Meta(PublishedModel.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shoppingcarts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_ShoppingCart')
        ]

    def __str__(self):
        return self.user
