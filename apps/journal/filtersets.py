from datetime import datetime, timedelta

from django_filters.rest_framework import FilterSet, filters

from apps.journal.models import TimeLog


class TimeLogFilerSet(FilterSet):
    date = filters.ChoiceFilter(
        choices=[('this_week', 'this_week'), ('this_month', 'this_month'), ('this_year', 'this_year')],
        method='filter_date')

    user_is_me = filters.BooleanFilter(method='filter_assigned_to_me')

    def filter_assigned_to_me(self, queryset, name, value):
        if value is True:
            return queryset.filter(user=self.request.user)
        if value is False:
            return queryset.exclude(user=self.request.user)
        return queryset

    def filter_date(self, queryset, name, value):
        if value == 'this_week':
            min_date_time = datetime.today() - timedelta(days=datetime.today().weekday() % 7)
            return queryset.filter(started_at__gte=min_date_time)
        if value == 'this_month':
            min_date_time = datetime.today().replace(day=1)
            return queryset.filter(started_at__gte=min_date_time)
        if value == 'this_year':
            min_date_time = datetime.today().replace(month=1, day=1)
            return queryset.filter(started_at__gte=min_date_time)
        return queryset

    class Meta:
        model = TimeLog
        fields = ('date', 'user_is_me')
