from rest_framework import serializers

from apps.task.models import Task, Comment


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description')
        extra_kwargs = {
            'assigned_to': {'read_only': True}
        }


class AllTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title')


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'assigned_to')


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description')
        extra_kwargs = {
            'title': {'write_only': True},
            'description': {'write_only': True}
        }


class TaskUpdateAssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)


class TaskUpdateUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content')


class AllCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)
