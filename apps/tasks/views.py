from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, mixins, viewsets, generics, filters
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested.viewsets import NestedViewSetMixin

from apps.tasks.models import Task, Comment
from apps.tasks.serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskAssignedToSerializer,
    AllTaskListSerializer,
    TaskStatusSerializer,
    CommentSerializer
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

    def get_serializer_class(self):
        if self.action == 'list':
            return AllTaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        return super(TaskViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)

    # Todo: this is an action and is more preferable if url will be a verb
    @action(methods=['patch'], detail=True, url_path='assign', serializer_class=TaskAssignedToSerializer)
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.assigned_to = serializer.validated_data.get('assigned_to')
        instance.save()
        self.send_task_assigned_email(instance.id, instance.assigned_to.email)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='complete', serializer_class=TaskStatusSerializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.send_task_completed_email(instance.id, instance.assigned_to.email)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='assigned', serializer_class=AllTaskListSerializer)
    def all_assigned_task(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(assigned_to=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='completed', serializer_class=AllTaskListSerializer)
    def all_completed_task(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(status=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @classmethod
    def send_task_completed_email(cls, task_id, recipient):
        send_mail('Task is completed',
                  f'Task {task_id} is completed', settings.EMAIL_HOST_USER, [recipient], fail_silently=False)

    @classmethod
    def send_task_assigned_email(cls, task_id, recipient):
        send_mail('Task is assigned',
                  f'Task {task_id} is assigned to you', settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


# Todo: task list
class CommentViewSet(NestedViewSetMixin, mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    def perform_create(self, serializer):
        serializer.save(task_id=self.kwargs.get('task_pk'))
        # Todo: there is wrong email
        self.send_task_created_email(serializer.data['id'], recipient=self.request.user.email)

    @classmethod
    def send_task_created_email(cls, task_id, recipient):
        send_mail('Your task is commented',
                  f'Your task with id {task_id} is commented',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
