from django.urls import path, include
from .views import (
    HabitListView, HabitCreateView, HabitUpdateView, HabitDeleteView,
    PublicHabitListView, HabitDetailView,
    HabitViewSet
)
from rest_framework.routers import DefaultRouter

app_name = 'habits'

# ViewSet для API
router = DefaultRouter()
router.register(r'', HabitViewSet, basename='habit')

urlpatterns = [
    # Веб-интерфейс
    path('', HabitListView.as_view(), name='habit_list'),
    path('public/', PublicHabitListView.as_view(), name='public_habits'),
    path('create/', HabitCreateView.as_view(), name='habit_create'),
    path('<int:pk>/', HabitDetailView.as_view(), name='habit_detail'),
    path('<int:pk>/update/', HabitUpdateView.as_view(), name='habit_update'),
    path('<int:pk>/delete/', HabitDeleteView.as_view(), name='habit_delete'),

    # API
    path('api/', include(router.urls)),
]