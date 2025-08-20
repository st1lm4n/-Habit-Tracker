from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView

from habits.views import PublicHabitListView


# Настройка Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="Atomic Habits API",
      default_version='v1',
      description="API for Atomic Habits Tracker",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@habits.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # Админ-панель
    path('admin/', admin.site.urls),

    # Веб-интерфейс
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    # API
    path('api/', include([
        path('auth/', include('rest_framework.urls')),
        path('users/', include('users.urls')),
        path('habits/', include('habits.urls')),
        path('public_habits/', PublicHabitListView.as_view(), name='api-public-habits'),
    ])),

    # Документация API
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Аутентификация
    path('auth/', include('django.contrib.auth.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
