from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_LENGT_EMAIL = 254
MAX_LENGT_USERNAME = 150


class UserProfile(AbstractUser):
    email = models.EmailField(
        unique=True, blank=True, max_length=MAX_LENGT_EMAIL)
    username = models.CharField(
        max_length=MAX_LENGT_USERNAME, blank=True, unique=True)

    class Meta:
        """Перевод модели"""

        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
