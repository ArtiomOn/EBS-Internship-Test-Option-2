from rest_framework import serializers

from apps.tasks.models import (
    Task,
    Comment
)


class TaskDetailSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'total_duration', 'assigned_to')


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'assigned_to')


class TaskAssignedToSerializer(serializers.ModelSerializer):
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
