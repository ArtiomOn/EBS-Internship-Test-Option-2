from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested.viewsets import NestedViewSetMixin
from rest_framework import (
    status,
    mixins,
    viewsets,
    filters
)

from apps.tasks.models import Task, Comment, TimeLog
from apps.tasks.filtersets import TaskFilterSet, TimeLogFilerSet
from apps.tasks.serializers import (
    TaskDetailSerializer,
    TaskAssignedToSerializer,
    TaskStatusSerializer,
    CommentSerializer,
    TaskCreateSerializer, TimeJournalSerializer, TimeLogListSerializer, TimeLogSerializer,
)


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilterSet
    ordering_fields = ['total_duration']
    search_fields = ['^title']

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(total_duration=Sum('time_logs__duration'))
        return super(TaskViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.action == 'create' or 'retrieve':
            return TaskCreateSerializer
        return super(TaskViewSet, self).get_serializer_class()

    @action(methods=['patch'], detail=True, url_path='assign',
            serializer_class=TaskAssignedToSerializer)
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.assigned_to = serializer.validated_data.get('assigned_to')
        instance.save()
        self.send_task_assigned_email(instance.id, instance.assigned_to.email)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='complete',
            serializer_class=TaskStatusSerializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.send_task_completed_email(instance.id, instance.assigned_to.email)
        return Response(status=status.HTTP_200_OK)

    @classmethod
    def send_task_completed_email(cls, task_id, recipient):
        send_mail('Task is completed',
                  f'Task {task_id} is completed',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)

    @classmethod
    def send_task_assigned_email(cls, task_id, recipient):
        send_mail('Task is assigned',
                  f'Task {task_id} is assigned to you',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


class CommentViewSet(
    NestedViewSetMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super(CommentViewSet, self).get_queryset()

    def perform_create(self, serializer):
        serializer.save(task_id=self.kwargs.get('task_pk'))
        self.send_task_created_email(serializer.data['id'], recipient=self.request.user.email)

    @classmethod
    def send_task_created_email(cls, task_id, recipient):
        send_mail('Your task is commented',
                  f'Your task with id {task_id} is commented',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


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
