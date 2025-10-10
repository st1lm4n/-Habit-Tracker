import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

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
        help_text="Имя пользователя в Telegram (без @)"
    )
    telegram_link_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name="Код привязки Telegram"
    )
    telegram_link_code_expires = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Срок действия кода привязки"
    )

    def __str__(self):
        return self.username

    def generate_link_code(self):
        """Генерация кода привязки с временем действия"""
        import random
        self.telegram_link_code = ''.join(random.choices('0123456789', k=6))
        self.telegram_link_code_expires = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.telegram_link_code

    def is_link_code_valid(self):
        """Проверка валидности кода привязки"""
        if not self.telegram_link_code or not self.telegram_link_code_expires:
            return False
        return timezone.now() < self.telegram_link_code_expires

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]