from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from .models import Habit
from .pagination import HabitPagination
from .permissions import IsOwner
from .serializers import HabitSerializer


class HabitViewSet(ModelViewSet):
    """
    list: Получение списка привычек текущего пользователя
    create: Создание новой привычки
    retrieve: Просмотр конкретной привычки
    update: Обновление привычки
    partial_update: Частичное обновление
    destroy: Удаление привычки
    """
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if self.action == 'list_public':
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitListView(ListAPIView):
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  # Разрешить доступ без авторизации
