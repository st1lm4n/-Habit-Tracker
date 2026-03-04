from django.urls import path
from .views import telegram_webhook, set_telegram_webhook

app_name = 'notifications'

urlpatterns = [
    # Вебхук для Telegram
    path('telegram/webhook/', telegram_webhook, name='telegram-webhook'),

    # Установка вебхука
    path('telegram/set-webhook/', set_telegram_webhook, name='set-telegram-webhook'),
]