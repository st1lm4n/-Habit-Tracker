from rest_framework.exceptions import ValidationError


def validate_related_habit_reward(attrs):
    if attrs.get('related_habit') and attrs.get('reward'):
        raise ValidationError("Нельзя указывать связанную привычку и вознаграждение одновременно")


def validate_pleasant_habit(attrs):
    if attrs.get('is_pleasant'):
        if attrs.get('reward') or attrs.get('related_habit'):
            raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки")


def validate_periodicity(value):
    if value > 7:
        raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней")


def validate_related_habit(value):
    if value and not value.is_pleasant:
        raise ValidationError("В связанные привычки можно добавлять только приятные привычки")


def validate_time_to_complete(value):
    """Проверка времени выполнения (не более 120 секунд)"""
    if value > 120:
        raise ValidationError("Время выполнения не должно превышать 120 секунд")
