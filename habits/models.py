from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.exceptions import ValidationError

from users.models import User


class Habit(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место"
    )
    time = models.TimeField(
        verbose_name="Время"
    )
    action = models.CharField(
        max_length=255,
        verbose_name="Действие"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,  # Разрешаем NULL значения
        blank=True,
        verbose_name="Связанная привычка"
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7)
        ],
        verbose_name="Периодичность (дни)"
    )
    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Вознаграждение"
    )
    time_to_complete = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(120)],
        verbose_name="Время на выполнение (секунды)"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичный доступ"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return f"{self.action} в {self.time} ({self.place})"

    def clean(self):
        # Валидация 1: Нельзя указывать и связанную привычку, и вознаграждение
        if self.related_habit and self.reward:
            raise ValidationError("Нельзя указывать одновременно связанную привычку и вознаграждение")

        # Валидация 2: Приятная привычка не может иметь вознаграждение или связанную привычку
        if self.is_pleasant:
            if self.related_habit or self.reward:
                raise ValidationError("Приятная привычка не может иметь связанную привычку или вознаграждение")

        # Валидация 3: Связанная привычка должна быть приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной")

        # Валидация 4: Нельзя ссылаться на себя
        if self.related_habit and self.related_habit == self:
            raise ValidationError("Нельзя ссылаться на себя как на связанную привычку")

        # Валидация 5: Периодичность 1-7 дней
        if self.periodicity < 1 or self.periodicity > 7:
            raise ValidationError("Периодичность должна быть от 1 до 7 дней")