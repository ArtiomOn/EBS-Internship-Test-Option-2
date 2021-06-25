from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.tasks.models import (
    Task,
    Comment,
    Timer
)


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ['id', 'title', 'description', 'status', 'assigned_to']


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['id', 'content', 'task']


@admin.register(Timer)
class TaskAdmin(ModelAdmin):
    list_display = ['id', 'execution_start', 'execution_end', 'real_time', 'root_task']
