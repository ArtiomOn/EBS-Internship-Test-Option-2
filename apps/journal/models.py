from django.db import models
from django.contrib.auth import get_user_model

from apps.tasks.models import Task

User = get_user_model()


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_logs')
    started_at = models.DateTimeField()
    duration = models.DurationField(null=True)

    def __str__(self):
        return f'{self.task}, {self.started_at}, {self.user}, {self.duration}'

    class Meta:
        verbose_name = 'Time log'
        verbose_name_plural = 'Time logs'
