from random import randrange, choice
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tasks.models import TimeLog, Task

User = get_user_model()


class Command(BaseCommand):
    help = "Create 50.000 random time logs"

    def _log_creating_notice(self, time):
        self.stdout.write(self.style.NOTICE(f'Time logs added in {time}'))

    def handle(self, *args, **options):
        data = []
        start = datetime.now()

        user_ids = User.objects.values_list('id', flat=True)
        task_ids = Task.objects.values_list('id', flat=True)
        for _ in range(50000):
            random_duration = randrange(10000)
            time_log = TimeLog(task_id=choice(task_ids),
                               user_id=choice(user_ids),
                               started_at=timezone.now(),
                               duration=str(random_duration))
            data.append(time_log)

        TimeLog.objects.bulk_create(data)
        end = datetime.now() - start
        self._log_creating_notice(end)
