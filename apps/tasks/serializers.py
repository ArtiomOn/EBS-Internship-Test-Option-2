from rest_framework import serializers

from apps.tasks.models import Task, Comment, TimeLog


class TaskSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField(required=False, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


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
    duration = serializers.DurationField()

    class Meta:
        model = TimeLog
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True},
            'user': {'read_only': True},
        }
