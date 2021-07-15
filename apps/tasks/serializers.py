from datetime import timedelta

from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from apps.tasks.documents import TaskDocument
from apps.tasks.models import Task, Comment, TimeLog


class TaskSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(required=False, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description')


class TaskAssignToSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True}
        }


class TimeLogSerializer(serializers.ModelSerializer):
    started_at = serializers.DateTimeField()
    duration = serializers.DurationField(read_only=True)
    minutes = serializers.IntegerField(write_only=True)

    def to_internal_value(self, data):
        value = super(TimeLogSerializer, self).to_internal_value(data)
        value['duration'] = timedelta(minutes=value.pop('minutes'))
        return value

    class Meta:
        model = TimeLog
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True},
            'user': {'read_only': True},
        }


class TaskDocumentSerializer(DocumentSerializer):
    class Meta:
        document = TaskDocument
        fields = '__all__'

