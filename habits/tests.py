from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status

from habits.models import Habit

class HabitModelTest(TestCase):
    def test_time_to_complete_max_value(self):
        habit = Habit(time_to_complete=121)
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_public_habits_access(self):
        response = self.client.get(reverse('public-habits'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

