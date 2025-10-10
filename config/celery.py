import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра объекта Celery
app = Celery('config')

# Загрузка настроек из файла settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из файлов tasks.py
# во всех установленных приложениях Django
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'send-habit-reminders-every-minute': {
        'task': 'notifications.tasks.send_telegram_reminder',
        'schedule': crontab(minute='*'),  # Каждую минуту
    },
}

# Тестовая задача для проверки работы Celery
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')