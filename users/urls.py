from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import SignUpView, ProfileView, CustomLoginView, RegisterAPIView
from .views import update_telegram_info

app_name = 'users'

urlpatterns = [
    # Веб-интерфейс
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('telegram/update/', update_telegram_info, name='update-telegram'),

    # API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', SignUpView.as_view(), name='api_register'),

    # Регистрация
    path('register/', RegisterAPIView.as_view(), name='api_register'),

    # Аутентификация JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

