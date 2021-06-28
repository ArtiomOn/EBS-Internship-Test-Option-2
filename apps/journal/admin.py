from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.journal.models import TimeLog


@admin.register(TimeLog)
class TimerAdmin(ModelAdmin):
    list_display = ['id', 'task', 'started_at', 'duration']
