from django.db import models
from apps.tasks.models import Task


class Timer(models.Model):
    execution_start = models.DateTimeField(auto_now_add=True, verbose_name='Start at:')
    execution_end = models.DateTimeField(auto_now=True, verbose_name='Finish at:')
    real_time = models.TimeField(null=True, blank=True, verbose_name='Average time')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_timer', verbose_name='Root task')

    def __str__(self):
        return f'{self.execution_start}, {self.execution_end}, {self.task}'

    class Meta:
        verbose_name = 'Timer'
        verbose_name_plural = 'Timers'
