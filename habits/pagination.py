from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator


class HabitPagination:
    """Пагинация для списка привычек"""

    def __init__(self, queryset, page_number, per_page=5):
        self.paginator = Paginator(queryset, per_page)
        self.page = self.paginator.get_page(page_number)

    @property
    def object_list(self):
        return self.page.object_list

    @property
    def pagination_data(self):
        return {
            'has_previous': self.page.has_previous(),
            'has_next': self.page.has_next(),
            'previous_page_number': self.page.previous_page_number() if self.page.has_previous() else None,
            'next_page_number': self.page.next_page_number() if self.page.has_next() else None,
            'page_number': self.page.number,
            'num_pages': self.page.paginator.num_pages,
        }