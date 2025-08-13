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


def validate_periodicity(value):
    if value < 1 or value > 7:
        raise ValidationError("Периодичность должна быть от 1 до 7 дней")


def validate_related_habit(value):
    if value and not value.is_pleasant:
        raise ValidationError(
            "Связанная привычка должна быть приятной!"
        )
    # Добавьте проверку на рекурсию
    if value and value.related_habit == value:
        raise ValidationError("Нельзя ссылаться на себя!")
