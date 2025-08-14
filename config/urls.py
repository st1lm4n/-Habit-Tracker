from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import include
from notifications import urls as notifications_urls
from habits.views import PublicHabitListView

# Настройка Swagger для документации API
schema_view = get_schema_view(
    openapi.Info(
        title="Atomic Habits API",
        default_version='v1',
        description="API for Atomic Habits Tracker",
        contact=openapi.Contact(email="support@atomichabits.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Админ-панель
    path('admin/', admin.site.urls),

    # Веб-интерфейс
    path('', include('core.urls')),

    # API
    path('api/', include([
        path('auth/', include('rest_framework.urls')),
        path('users/', include('users.urls')),
        path('habits/', include('habits.urls')),
        path('public_habits/', PublicHabitListView.as_view(), name='api-public-habits'),
    ])),

    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Аутентификация
    path('auth/', include('django.contrib.auth.urls')),

    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
