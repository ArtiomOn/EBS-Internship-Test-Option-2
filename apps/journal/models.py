from django.db import models
from django.db.models import CASCADE

from apps.tasks.models import Task


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=CASCADE, related_name='time_logs')
    started_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True)

    def __str__(self):
        return f'{self.task}, {self.started_at}, {self.duration}'

    class Meta:
        verbose_name = 'Time log'
        verbose_name_plural = 'Time logs'
