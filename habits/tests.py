from django.test import TestCase
from django.core.exceptions import ValidationError
from habits.models import Habit

class HabitModelTest(TestCase):
    def test_time_to_complete_max_value(self):
        habit = Habit(time_to_complete=121)
        with self.assertRaises(ValidationError):
            habit.full_clean()