from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

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


from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import Habit
from .forms import HabitForm


class HabitListView(LoginRequiredMixin, ListView):
    """Список привычек текущего пользователя"""
    model = Habit
    template_name = 'habits/habit_list.html'
    context_object_name = 'habits'
    paginate_by = 5  # Пагинация по 5 привычек на страницу

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by('-created_at')


class HabitDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр привычки"""
    model = Habit
    template_name = 'habits/habit_detail.html'
    context_object_name = 'habit'

    def get_object(self, queryset=None):
        habit = super().get_object(queryset)
        if habit.user != self.request.user and not habit.is_public:
            raise PermissionDenied("У вас нет доступа к этой привычке")
        return habit


class HabitCreateView(LoginRequiredMixin, CreateView):
    """Создание новой привычки"""
    model = Habit
    form_class = HabitForm
    template_name = 'habits/habit_form.html'
    success_url = reverse_lazy('habit_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить новую привычку'
        return context


class HabitUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование существующей привычки"""
    model = Habit
    form_class = HabitForm
    template_name = 'habits/habit_form.html'
    success_url = reverse_lazy('habit_list')

    def get_object(self, queryset=None):
        habit = super().get_object(queryset)
        if habit.user != self.request.user:
            raise PermissionDenied("Вы не можете редактировать чужую привычку")
        return habit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать привычку'
        return context


class HabitDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление привычки"""
    model = Habit
    template_name = 'habits/habit_confirm_delete.html'
    success_url = reverse_lazy('habit_list')

    def get_object(self, queryset=None):
        habit = super().get_object(queryset)
        if habit.user != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужую привычку")
        return habit


class PublicHabitListView(ListView):
    """Список публичных привычек"""
    model = Habit
    template_name = 'habits/public_habits.html'
    context_object_name = 'public_habits'
    paginate_by = 10
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).order_by('-created_at')
