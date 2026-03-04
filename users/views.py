import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .forms import CustomUserCreationForm, UserProfileForm
from .models import User
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()


class SignUpView(CreateView):
    """Регистрация нового пользователя"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('habit_list')

    def form_valid(self, form):
        # При обновлении Telegram username
        new_telegram_username = form.cleaned_data.get('telegram_username')
        user = self.request.user

        # Если Telegram username изменился
        if new_telegram_username != user.telegram_username:
            user.telegram_username = new_telegram_username
            user.telegram_chat_id = None  # Сбрасываем chat_id
            user.save()

        return super().form_valid(form)

    def generate_telegram_code(request):
        """Генерация нового кода привязки Telegram"""
        if not request.user.is_authenticated:
            return redirect('login')

        request.user.generate_link_code()
        return redirect('profile')


class CustomLoginView(LoginView):
    """Кастомный вход в систему с обработкой Telegram"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)

        # Проверяем наличие telegram_username для автоматического получения chat_id
        if self.request.user.telegram_username and not self.request.user.telegram_chat_id:
            update_telegram_info(self.request, self.request.user.telegram_username)

        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    """Профиль пользователя"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # При обновлении Telegram username пытаемся получить chat_id
        telegram_username = form.cleaned_data.get('telegram_username')
        if telegram_username and telegram_username != self.request.user.telegram_username:
            update_telegram_info(self.request, telegram_username)

        return super().form_valid(form)


class RegisterAPIView(generics.CreateAPIView):
    """API для регистрации пользователя"""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User created successfully",
        }, status=status.HTTP_201_CREATED)


def update_telegram_info(request, telegram_username):
    """
    Обновление информации Telegram для пользователя
    :param request: HttpRequest
    :param telegram_username: Имя пользователя в Telegram
    """
    from config import settings
    user = request.user

    # Если chat_id уже есть, пропускаем
    if user.telegram_chat_id:
        return

    # Форматируем username (убираем @ если есть)
    telegram_username = telegram_username.lstrip('@')

    try:
        # Получаем информацию о пользователе через Telegram API
        response = requests.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/getUpdates"
        )
        response.raise_for_status()
        updates = response.json().get('result', [])

        # Ищем пользователя в обновлениях
        for update in updates:
            message = update.get('message', {})
            from_user = message.get('from', {})
            chat = message.get('chat', {})

            if from_user.get('username') == telegram_username:
                user.telegram_chat_id = chat.get('id')
                user.telegram_username = telegram_username
                user.save()
                return

        # Если не нашли в существующих обновлениях, отправляем инструкцию
        message = (
            "Для завершения привязки Telegram аккаунта:\n"
            "1. Перейдите в бота @AtomicHabitsTrackerBot\n"
            "2. Отправьте команду /start\n"
            "3. Нажмите кнопку 'Привязать аккаунт'"
        )
        request.session['telegram_message'] = message

    except Exception as e:
        # Логируем ошибку, но не прерываем работу
        print(f"Ошибка при обновлении Telegram: {e}")


def telegram_webhook(request):
    """Обработчик вебхука Telegram"""
    from config import settings
    from django.http import JsonResponse

    if request.method == 'POST':
        try:
            data = request.json()
            message = data.get('message', {})
            chat = message.get('chat', {})
            text = message.get('text', '').strip().lower()

            # Обработка команды /start
            if text == '/start':
                response_text = (
                    "Привет! Я бот для трекера привычек Atomic Habits.\n\n"
                    "Чтобы привязать аккаунт, нажмите кнопку ниже."
                )

                # Отправка сообщения с кнопкой
                requests.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
                    json={
                        'chat_id': chat['id'],
                        'text': response_text,
                        'reply_markup': {
                            'inline_keyboard': [[
                                {
                                    'text': 'Привязать аккаунт',
                                    'callback_data': 'link_account'
                                }
                            ]]
                        }
                    }
                )

            # Обработка callback от кнопки
            elif data.get('callback_query'):
                callback = data['callback_query']
                if callback.get('data') == 'link_account':
                    # Здесь должна быть логика привязки аккаунта
                    # В реальной реализации мы бы отправили код привязки
                    requests.post(
                        f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
                        json={
                            'chat_id': callback['message']['chat']['id'],
                            'text': "Введите ваш код привязки из личного кабинета:"
                        }
                    )

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            print(f"Ошибка в телеграм вебхуке: {e}")
            return JsonResponse({'status': 'error'}, status=500)

    return JsonResponse({'status': 'method not allowed'}, status=405)
