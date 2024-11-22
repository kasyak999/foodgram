from django.contrib.auth.models import AbstractUser
from django.db import models
from project.settings import MAX_LENGT_EMAIL, MAX_LENGT_USERNAME
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class UserProfile(AbstractUser):
    email = models.EmailField(
        unique=True, blank=True, max_length=MAX_LENGT_EMAIL)
    username = models.CharField(
        max_length=MAX_LENGT_USERNAME, blank=True, unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message=(
                    'Имя пользователя может содержать только латинские '
                    'буквы, цифры и символ подчеркивания.'),
                code='invalid_username'
            )
        ]
    )
    avatar = models.ImageField(
        upload_to='users/', null=True, blank=True, default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        """Перевод модели"""

        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Подписки пользователей"""
    following = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='following',
        verbose_name='на кого подписан')
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='follower',
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

    def clean(self):
        if self.user == self.following:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def __str__(self):
        return f'Подписчик {self.user}'
