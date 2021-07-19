import string
import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Create 25.000 random tasks"

    def _log_creating_notice(self, time):
        self.stdout.write(self.style.NOTICE(f'Items added in {time}'))

    def handle(self, *args, **options):
        random_letters = string.ascii_letters

        data = []
        start = datetime.now()
        user_ids = User.objects.values_list('id', flat=True)
        for _ in range(50000):
            random_title = (''.join(random.choice(random_letters) for _ in range(20)))
            random_description = (''.join(random.choice(random_letters) for _ in range(60)))
            data.append(Task(title=random_title, description=random_description, assigned_to_id=random.choice(user_ids)))
        Task.objects.bulk_create(data)
        end = datetime.now() - start
        self._log_creating_notice(end)
