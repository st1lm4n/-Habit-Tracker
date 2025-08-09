from celery import shared_task
import requests
from habits.models import Habit
from django.utils import timezone
from datetime import timedelta
from config import settings


@shared_task
def send_telegram_reminder():
    now = timezone.now()
    start_time = now - timedelta(minutes=1)
    end_time = now + timedelta(minutes=1)

    habits = Habit.objects.filter(
        time__range=(start_time.time(), end_time.time())
    )

    for habit in habits:
        chat_id = habit.user.telegram_chat_id
        if chat_id:
            message = (
                f"Напоминание о привычке!\n"
                f"Действие: {habit.action}\n"
                f"Место: {habit.place}\n"
                f"Время: {habit.time.strftime('%H:%M')}\n"
                f"Время на выполнение: {habit.time_to_complete} сек"
            )
            requests.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
                data={
                    'chat_id': chat_id,
                    'text': message
                }
            )