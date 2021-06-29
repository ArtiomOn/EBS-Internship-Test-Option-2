from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested.viewsets import NestedViewSetMixin
from rest_framework import (
    status,
    mixins,
    viewsets,
    generics,
    filters
)

from apps.tasks.models import Task, Comment
from apps.tasks.filtersets import TaskFilterSet
from apps.tasks.serializers import (
    TaskDetailSerializer,
    TaskAssignedToSerializer,
    TaskStatusSerializer,
    CommentSerializer, TaskAmountSerializer,
)


class TaskFilterListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^title']


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilterSet
    ordering_fields = ['total_duration']

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(total_duration=Sum('time_logs__duration'))
        return super(TaskViewSet, self).get_queryset()

    @action(methods=['get'], detail=False, url_path='amount',
            serializer_class=TaskAmountSerializer)
    def task_amount(self, request, *args, **kwargs):
        instance = Task.objects.all().annotate(total_duration=Sum('time_logs__duration'))
        queryset = instance.order_by('-total_duration')[:20]

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
