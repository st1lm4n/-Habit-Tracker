import logging

import requests
from celery import shared_task
from django.utils import timezone

from config import settings
from habits.models import Habit

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_reminder():
    try:
        now = timezone.localtime()
        current_time = now.time().replace(second=0, microsecond=0)

        habits = Habit.objects.filter(
            time__hour=current_time.hour,
            time__minute=current_time.minute
        ).select_related('user')

        for habit in habits:
            chat_id = habit.user.telegram_chat_id
            if chat_id:
                message = (
                    f"⏰ Напоминание о привычке!\n"
                    f"▶ Действие: {habit.action}\n"
                    f"📍 Место: {habit.place}\n"
                    f"🕒 Время: {habit.time.strftime('%H:%M')}\n"
                    f"⏱ Время на выполнение: {habit.time_to_complete} сек"
                )
                try:
                    response = requests.post(
                        f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
                        json={
                            'chat_id': chat_id,
                            'text': message,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                    response.raise_for_status()
                    logger.info(f"Reminder sent to {habit.user} for habit {habit.id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки в Telegram: {e}")
    except Exception as e:
        logger.error(f"Ошибка в задаче send_telegram_reminder: {e}")
