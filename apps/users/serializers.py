from apps.task.models import Task
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = User
        fields = ('id', 'full_name')


class TaskCurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title')
