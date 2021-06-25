from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from apps.journal.models import Timer
from apps.journal.serializers import TimerSerializer, TimerDetailSerializer


class TimerViewSet(NestedViewSetMixin,
                   GenericViewSet):
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer
    permission_classes = [IsAuthenticated]

    parent_lookup_kwargs = {
        'task_pk': 'task__pk',
    }

    @action(methods=['post'], detail=False, url_path='start')
    def create_timer(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task_id=self.kwargs.get('task_pk'))
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['patch'], detail=True, url_path='stop', serializer_class=TimerDetailSerializer)
    def stop_timer(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
