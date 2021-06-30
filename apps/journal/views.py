from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin
from rest_framework.exceptions import NotFound

from apps.journal.models import TimeLog
from apps.journal.filtersets import TimeLogFilerSet
from apps.journal.serializers import (
    TimeLogSerializer,
    TimeJournalSerializer,
    TimeLogListSerializer,
)


class TimerViewSet(
    NestedViewSetMixin,
    GenericViewSet
):
    queryset = TimeLog.objects.all()
    serializer_class = TimeJournalSerializer
    permission_classes = [IsAuthenticated]

    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    @action(methods=['get'], detail=False, url_path='list',
            serializer_class=TimeLogListSerializer)
    def time_log_list(self, request, *args, **kwargs):
        queryset = TimeLog.objects.annotate(total_duration=Sum('duration'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'))
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='detail',
            serializer_class=TimeJournalSerializer)
    def create_time_journal(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'),
                        duration=timedelta(minutes=request.data['minutes']))
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='start',
            serializer_class=TimeLogSerializer)
    def time_log_start(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'),
                        started_at=timezone.now(), user=request.user)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['patch'], detail=False, url_path='stop',
            serializer_class=TimeLogSerializer)
    def time_log_stop(self, request, *args, **kwargs):
        instance = TimeLog.objects.filter(duration=None, user=request.user).first()
        if instance is None:
            raise NotFound()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(duration=timezone.now() - instance.started_at)
        return Response(status=status.HTTP_200_OK)


class TimeLogViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = TimeLog.objects.all()
    serializer_class = TimeJournalSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TimeLogFilerSet
