from django.utils import timezone
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin
from rest_framework.exceptions import NotFound

from apps.journal.models import TimeLog
from apps.journal.serializers import TimeLogSerializer, TimeLogDetailSerializer
from apps.tasks.models import Task


class TimerViewSet(NestedViewSetMixin,
                   GenericViewSet):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAuthenticated]

    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super(TimerViewSet, self).get_queryset()

    @action(methods=['post'], detail=False, url_path='start')
    def time_log_start(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'))
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
