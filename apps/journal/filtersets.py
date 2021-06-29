from django_filters.rest_framework import FilterSet, filters

from apps.journal.models import TimeLog


class TimeLogFilerSet(FilterSet):
    month = filters.NumberFilter(field_name='started_at', lookup_expr='month')
    is_assigned_to_me = filters.BooleanFilter(method='filter_assigned_to_me')

    def filter_assigned_to_me(self, queryset, name, value):
        if value is True:
            return queryset.filter(user=self.request.user)
        if value is False:
            return queryset.exclude(user=self.request.user)
        return queryset

    class Meta:
        model = TimeLog
        fields = ('month',)
