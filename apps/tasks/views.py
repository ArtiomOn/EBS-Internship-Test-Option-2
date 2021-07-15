from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum, QuerySet
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet

from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
    IdsFilterBackend
)
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin
from rest_framework import (
    status,
    mixins,
    viewsets,
    filters
)

from apps.tasks.filtersets import TaskFilterSet, TimeLogFilerSet
from apps.tasks.models import Task, Comment, TimeLog
from apps.tasks.documents import TaskDocument
from apps.tasks.permissions import IsOwner
from apps.tasks.search import search
from apps.tasks.serializers import (
    TaskSerializer,
    TaskAssignToSerializer,
    TaskStatusSerializer,
    CommentSerializer,
    TimeLogSerializer,
    TaskCreateSerializer,
    TaskDocumentSerializer,
)


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilterSet
    ordering_fields = ['total_duration']
    search_fields = ['^title']

    def get_permissions(self):
        if self.action in ('create', 'list', 'retrieve'):
            self.permission_classes = [IsAuthenticated]
        if self.action == 'destroy':
            self.permission_classes = [IsOwner]
        return super(TaskViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(total_duration=Sum('time_logs__duration'))
        return super(TaskViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskSerializer
        if self.action == 'create':
            return TaskCreateSerializer
        return super(TaskViewSet, self).get_serializer_class()

    @action(methods=['patch'], detail=True, url_path='assign', serializer_class=TaskAssignToSerializer,
            permission_classes=[IsAdminUser])
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.assigned_to = serializer.validated_data.get('assigned_to')
        instance.save()
        self.send_task_assigned_email(instance.id, instance.assigned_to.email)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='complete', serializer_class=TaskStatusSerializer,
            permission_classes=[IsAdminUser])
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


class TaskCommentViewSet(
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
        return super(TaskCommentViewSet, self).get_queryset()

    def perform_create(self, serializer):
        serializer.save(task_id=self.kwargs.get('task_pk'))
        self.send_task_created_email(serializer.data['id'], recipient=self.request.user.email)

    @classmethod
    def send_task_created_email(cls, task_id, recipient):
        send_mail('Your task is commented',
                  f'Your task with id {task_id} is commented',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


class TaskTimeLogViewSet(
    NestedViewSetMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAdminUser]
    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    def get_permissions(self):
        if self.action in ('list', 'create'):
            self.permission_classes = [IsAuthenticated]
        return super(TaskTimeLogViewSet, self).get_permissions()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super(TaskTimeLogViewSet, self).get_queryset()

    def perform_create(self, serializer):
        serializer.save(
            task_id=self.kwargs.get('task_pk'),
            user=self.request.user
        )

    @action(methods=['get'], detail=False, url_path='start')
    def start(self, request, *args, **kwargs):
        queryset: QuerySet = self.get_queryset()
        queryset.update_or_create(
            user=self.request.user,
            duration=None,
            defaults={
                'started_at': timezone.now(),
                'task_id': self.kwargs.get('task_pk')
            }
        )

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, url_path='stop')
    def stop(self, request, *args, **kwargs):
        queryset: QuerySet = self.get_queryset()
        instance = queryset.filter(duration=None, user=request.user).first()
        if instance is None:
            raise NotFound()

        instance.duration = timezone.now() - instance.started_at
        instance.save()

        return Response(status=status.HTTP_200_OK)


class TimeLogViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TimeLogFilerSet

    @method_decorator(cache_page(60 * 1))
    def list(self, request, *args, **kwargs):
        return super(TimeLogViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        return self.filter_queryset(TimeLog.objects.all().order_by('-duration'))[:20]


class TaskSearchViewSet(BaseDocumentViewSet):
    document = TaskDocument
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDocumentSerializer
    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    filter_fields = {
        'title': {
            'field': 'title',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'description': {
            'field': 'description',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
    }

    ordering_fields = {
        'id': None,
        'title': None,
    }

    def get_queryset(self):
        q = self.request.query_params.get('q')
        if q is not None:
            return search(q)
        return super().get_queryset()
