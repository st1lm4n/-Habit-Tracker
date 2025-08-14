from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя с полями для Telegram"""
    telegram_username = forms.CharField(
        max_length=100,
        required=False,
        label='Telegram Username',
        help_text='Без @, например: mytelegram'
    )
    telegram_chat_id = forms.CharField(
        max_length=30,
        required=False,
        label='Telegram Chat ID',
        help_text='Опционально, можно оставить пустым'
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name',
            'telegram_username', 'telegram_chat_id'
        )


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'telegram_username', 'telegram_chat_id'
        )
        labels = {
            'telegram_username': 'Telegram Username',
            'telegram_chat_id': 'Telegram Chat ID'
        }
        help_texts = {
            'telegram_username': 'Без @, например: mytelegram',
            'telegram_chat_id': 'ID чата в Telegram'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
