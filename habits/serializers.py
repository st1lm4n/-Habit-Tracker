from rest_framework import serializers
from .models import Habit
from .validators import *


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'time_to_complete': {'help_text': 'В секундах (макс. 120)'},
            'periodicity': {'help_text': 'Периодичность в днях (1-7)'}
        }

    def validate(self, attrs):
        validate_related_habit_reward(attrs)
        validate_pleasant_habit(attrs)

        if 'periodicity' in attrs:
            validate_periodicity(attrs['periodicity'])

        if 'related_habit' in attrs and attrs['related_habit']:
            validate_related_habit(attrs['related_habit'])

        return attrs