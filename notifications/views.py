import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import User
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def telegram_webhook(request):
    """
    Обработчик входящих обновлений от Telegram
    """
    if request.method == 'POST':
        try:
            data = request.json()
            logger.debug(f"Received Telegram update: {data}")

            # Обработка сообщений
            if 'message' in data:
                return handle_message(data['message'])

            # Обработка callback от кнопок
            if 'callback_query' in data:
                return handle_callback(data['callback_query'])

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            logger.error(f"Error in telegram_webhook: {e}")
            return JsonResponse({'status': 'error'}, status=500)

    return JsonResponse({'status': 'method not allowed'}, status=405)


def handle_message(message):
    """Обработка входящих сообщений"""
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    # Обработка команды /start
    if text == '/start':
        response_text = (
            "👋 Привет! Я бот для трекера привычек Atomic Habits.\n\n"
            "Я буду напоминать тебе о твоих привычках в нужное время.\n\n"
            "Чтобы привязать свой аккаунт, нажми кнопку ниже 👇"
        )

        # Отправка сообщения с кнопкой
        send_telegram_message(
            chat_id,
            response_text,
            reply_markup={
                'inline_keyboard': [[
                    {
                        'text': 'Привязать аккаунт',
                        'callback_data': 'link_account'
                    }
                ]]
            }
        )
        return JsonResponse({'status': 'ok'})

    # Обработка кода привязки (6-значный код)
    elif text.isdigit() and len(text) == 6:
        return link_account_by_code(chat_id, text)

    # Ответ по умолчанию
    default_response = (
        "🤖 Я пока не понимаю эту команду.\n\n"
        "Используй /start для начала работы."
    )
    send_telegram_message(chat_id, default_response)
    return JsonResponse({'status': 'ok'})


def handle_callback(callback_query):
    """Обработка callback от inline кнопок"""
    message = callback_query['message']
    chat_id = message['chat']['id']
    data = callback_query['data']

    if data == 'link_account':
        # Генерация уникального кода
        import random
        code = ''.join(random.choices('0123456789', k=6))

        # Сохраняем код в базе данных (временное решение)
        # В реальном приложении нужно связать код с пользователем
        user, created = User.objects.get_or_create(
            telegram_chat_id=chat_id,
            defaults={'telegram_link_code': code}
        )
        if not created:
            user.telegram_link_code = code
            user.save()

        response_text = (
            "🔑 Для привязки аккаунта:\n\n"
            "1. Перейди в свой профиль в веб-приложении\n"
            "2. В разделе Telegram введи этот код:\n\n"
            f"<b>{code}</b>\n\n"
            "⚠️ Код действителен 10 минут"
        )

        send_telegram_message(
            chat_id,
            response_text,
            parse_mode='HTML'
        )

        # Ответ на callback, чтобы убрать "часики" у кнопки
        answer_callback_query(callback_query['id'])
        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'unknown callback'})


def link_account_by_code(chat_id, code):
    """Привязка аккаунта по коду"""
    try:
        user = User.objects.get(telegram_link_code=code)
        user.telegram_chat_id = chat_id
        user.telegram_link_code = None
        user.save()

        response_text = (
            "✅ Аккаунт успешно привязан!\n\n"
            f"Привет, {user.username}!\n"
            "Теперь ты будешь получать напоминания о своих привычках."
        )

        send_telegram_message(chat_id, response_text)
        return JsonResponse({'status': 'ok'})

    except User.DoesNotExist:
        response_text = (
            "❌ Неверный код привязки.\n\n"
            "Проверь код и попробуй еще раз.\n"
            "Если проблема сохраняется, запроси новый код через веб-интерфейс."
        )
        send_telegram_message(chat_id, response_text)
        return JsonResponse({'status': 'invalid code'})

    except Exception as e:
        logger.error(f"Error linking account: {e}")
        response_text = "⚠️ Произошла ошибка. Пожалуйста, попробуй позже."
        send_telegram_message(chat_id, response_text)
        return JsonResponse({'status': 'error'}, status=500)


def send_telegram_message(chat_id, text, parse_mode=None, reply_markup=None):
    """Отправка сообщения через Telegram API"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }

    if reply_markup:
        payload['reply_markup'] = reply_markup

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return None


def answer_callback_query(callback_query_id):
    """Ответ на callback query (убирает 'часики')"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_query_id
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")


def set_telegram_webhook(request):
    """Установка вебхука для Telegram бота"""
    if not settings.TELEGRAM_TOKEN:
        return HttpResponse("TELEGRAM_TOKEN не настроен", status=500)

    # URL вашего вебхука (должен быть HTTPS)
    webhook_url = f"{settings.BASE_URL}/notifications/telegram/webhook/"

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/setWebhook"
    payload = {
        'url': webhook_url
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get('ok'):
            return HttpResponse(
                f"Вебхук успешно установлен: {webhook_url}\n\n"
                f"Ответ Telegram: {result['description']}",
                status=200
            )
        else:
            return HttpResponse(
                f"Ошибка установки вебхука: {result.get('description')}",
                status=500
            )

    except Exception as e:
        return HttpResponse(
            f"Ошибка при установке вебхука: {str(e)}",
            status=500
        )