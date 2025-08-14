from django.urls import path
from .views import SignUpView, ProfileView, CustomLoginView, update_telegram_info

app_name = 'users'

urlpatterns = [
    # Веб-интерфейс
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('telegram/update/', update_telegram_info, name='update-telegram'),

    # API
    path('api/register/', SignUpView.as_view(), name='api-register'),
]