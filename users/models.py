from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    telegram_chat_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Telegram Chat ID",
        help_text="ID чата в Telegram для отправки уведомлений"
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Telegram Username",
        help_text="Имя пользователя в Telegram"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]