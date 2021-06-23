from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_nested.viewsets import NestedViewSetMixin

from apps.task.models import Task, Comment
from apps.task.serializers import (
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateAssignedUserSerializer,
    AllTaskListSerializer,
    TaskUpdateStatusSerializer,
    CreateCommentSerializer,
    AllCommentSerializer
)


class TaskViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
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

    @action(methods=['patch'], detail=True, url_path='complete', serializer_class=TaskUpdateStatusSerializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.status = True
        instance.save()

        return Response({
            'id': instance.id,
            'status': instance.status
        })

    @action(methods=['get'], detail=False, url_path='assigned', serializer_class=AllTaskListSerializer)
    def assigned_task(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(assigned_to=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='completed', serializer_class=AllTaskListSerializer)
    def completed_task(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(status=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=True, url_path='assigned', serializer_class=TaskUpdateAssignedUserSerializer)
    def assigned_task_change(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.assigned_to = serializer.validated_data.get('assigned_to')
        instance.save()
        return Response(status=status.HTTP_200_OK)


class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = AllCommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }


