from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPagination
from .permissions import IsOwner


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