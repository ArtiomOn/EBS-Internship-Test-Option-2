from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.journal.models import Timer


@admin.register(Timer)
class TimerAdmin(ModelAdmin):
    list_display = ['id', 'execution_start', 'execution_end', 'real_time', 'task']
