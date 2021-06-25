from django_filters.rest_framework import FilterSet, filters

from apps.tasks.models import Task


class TaskFilterSet(FilterSet):
    is_assigned_to_me = filters.BooleanFilter(method='filter_assigned_to_me')
    is_completed = filters.BooleanFilter(field_name='status')

    def filter_assigned_to_me(self, queryset, name, value):
        if value is True:
            return queryset.filter(assigned_to=self.request.user)
        if value is False:
            return queryset.exclude(assigned_to=self.request.user)
        return queryset

    class Meta:
        model = Task
        fields = ('is_assigned_to_me', 'is_completed')
