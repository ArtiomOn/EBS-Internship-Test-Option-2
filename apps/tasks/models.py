from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=155)
    description = models.CharField(max_length=255)
    status = models.BooleanField(default=False, verbose_name='Completed')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')

    def __str__(self):
        return f'{self.title}, {self.description}, {self.status}, {self.assigned_to}'

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class Comment(models.Model):
    content = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class Timer(models.Model):
    execution_start = models.DateTimeField(auto_now_add=True, verbose_name='Start at:')
    execution_end = models.DateTimeField(auto_now=True, verbose_name='Finish at:')
    real_time = models.TimeField(null=True, verbose_name='Real time', blank=True)
    root_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_timer', verbose_name='Root task')

    def __str__(self):
        return f'{self.execution_start}, {self.execution_start}'

    class Meta:
        verbose_name = 'Timer'
        verbose_name_plural = 'Timers'
