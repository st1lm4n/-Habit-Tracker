from django import forms
from django.db.models import Q

from .models import Habit
from .validators import validate_related_habit, validate_periodicity, validate_time_to_complete


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = [
            'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'periodicity', 'reward',
            'time_to_complete', 'is_public'
        ]
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'related_habit': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'is_pleasant': 'Это приятная привычка',
            'is_public': 'Сделать публичной'
        }
        help_texts = {
            'periodicity': 'Периодичность выполнения в днях (1-7)',
            'time_to_complete': 'Время на выполнение в секундах (макс. 120)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Фильтрация связанных привычек (только приятные)
        self.fields['related_habit'].queryset = Habit.objects.filter(is_pleasant=True)

        # Если передан пользователь, фильтруем его привычки
        if user:
            self.fields['related_habit'].queryset = self.fields['related_habit'].queryset.filter(
                Q(user=user) | Q(is_public=True))

    def clean(self):
        cleaned_data = super().clean()

        # Валидация 1: Нельзя указывать и связанную привычку, и вознаграждение
        related_habit = cleaned_data.get('related_habit')
        reward = cleaned_data.get('reward')
        is_pleasant = cleaned_data.get('is_pleasant')

        if related_habit and reward:
            raise forms.ValidationError(
                "Нельзя указывать одновременно связанную привычку и вознаграждение"
            )

        # Валидация 2: Приятная привычка не может иметь вознаграждение или связанную привычку
        if is_pleasant:
            if related_habit or reward:
                raise forms.ValidationError(
                    "Приятная привычка не может иметь связанную привычку или вознаграждение"
                )

        # Валидация 3: Связанная привычка должна быть приятной
        if related_habit and not related_habit.is_pleasant:
            raise forms.ValidationError(
                "Связанная привычка должна быть приятной"
            )

        # Валидация 4: Нельзя ссылаться на себя
        if self.instance and related_habit and related_habit.id == self.instance.id:
            raise forms.ValidationError(
                "Нельзя ссылаться на себя как на связанную привычку"
            )

        # Валидация отдельных полей
        validate_periodicity(cleaned_data.get('periodicity'))
        validate_time_to_complete(cleaned_data.get('time_to_complete'))

        return cleaned_data