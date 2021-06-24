from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.tasks.models import Task, Comment


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ['id', 'title', 'description', 'status', 'assigned_to']


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['id', 'content', 'task']
