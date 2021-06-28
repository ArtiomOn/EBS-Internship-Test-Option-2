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
from apps.journal.serializers import (
    TimeLogSerializer,
    TimeLogDetailSerializer,
    TimeJournalSerializer,
    TimeJournalListSerializer,
    TimeProfileListSerializer
)
from apps.tasks.models import Task


class TimerViewSet(NestedViewSetMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = TimeLog.objects.all()
    serializer_class = TimeJournalSerializer
    permission_classes = [IsAuthenticated]

    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super(TimerViewSet, self).get_queryset()

    @action(methods=['get'], detail=False, url_path='profile', serializer_class=TimeProfileListSerializer)
    def time_profile_list(self, request, *args, **kwargs):
        queryset = TimeLog.objects.annotate(total_duration=Sum('duration'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='detail', serializer_class=TimeJournalSerializer)
    def time_journal_detail(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'), duration=timedelta(minutes=request.data['minutes']))
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='start', serializer_class=TimeLogSerializer)
    def time_log_start(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'), started_at=timezone.now())
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['patch'], detail=False, url_path='stop', serializer_class=TimeLogDetailSerializer)
    def time_log_duration(self, request, *args, **kwargs):
        instance = TimeLog.objects.filter(duration=None).first()
        if instance is None:
            raise NotFound()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(duration=timezone.now() - instance.started_at)
        return Response(status=status.HTTP_200_OK)
