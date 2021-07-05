from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.tasks.models import Task, Comment, TimeLog

User = get_user_model()


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
    }


class TaskTestCase(APITestCase):
    def setUp(self):
        # Create simple user
        self.simple_user = User.objects.create(
            email='simple@test.com',
            first_name='simple_first_name',
            last_name='simple_last_name',
            username='simple@test.com',
            is_superuser=False,
            is_staff=False,
        )
        self.password = self.simple_user.set_password('simple')
        self.simple_user.save()

        # Create admin user
        self.admin_user = User.objects.create(
            email='admin@test.com',
            first_name='admin_first_name',
            last_name='admin_last_name',
            username='admin@test.com',
            is_superuser=True,
            is_staff=True,
        )
        self.password = self.admin_user.set_password('admin')
        self.admin_user.save()

        # Create task for admin user
        self.task_admin = Task.objects.create(
            title='admin_title',
            description='admin_description',
            status=False,
            assigned_to=self.admin_user
        )
        self.task_admin.save()

        # Create task for simple user
        self.task_simple_user = Task.objects.create(
            title='simple_title',
            description='simple_description',
            status=False,
            assigned_to=self.simple_user
        )
        self.task_simple_user.save()

    # Create task by simple user
    def test_simple_user_task_create(self):
        create = self.client.post('/tasks/', data={
            'title': 'test_title',
            'description': 'test_description',
            'assigned_to': self.simple_user
        }, **auth(self.simple_user))
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)

    # Create task by admin
    def test_admin_user_task_create(self):
        create = self.client.post('/tasks/', data={
            'title': 'title_title',
            'description': 'test_description',
            'assigned_to': self.admin_user
        }, **auth(self.admin_user))
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)

    # Get list of tasks by admin
    def test_admin_user_task_list(self):
        response = self.client.get('/tasks/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Get list of tasks by simple user
    def test_simple_user_task_list(self):
        response = self.client.get('/tasks/', data={'assigned_to': self.simple_user}, **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Get list of task by id by admin user
    def test_admin_user_task_detail(self):
        response = self.client.get(f'/tasks/{self.task_admin.pk}/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Get list of task by id by simple user
    def test_simple_user_task_detail(self):
        response = self.client.get(f'/tasks/{self.task_simple_user.pk}/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Delete task by id by admin
    def test_admin_user_task_delete(self):
        response = self.client.delete(f'/tasks/{self.task_admin.pk}/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Delete task by id by user owner
    def test_owner_user_task_delete(self):
        response = self.client.delete(f"/tasks/{self.task_simple_user.pk}/", **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Delete task by id by simple user
    def test_simple_user_task_delete(self):
        response = self.client.delete(f'/tasks/{self.task_admin.pk}/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Change task assign by admin user
    def test_admin_user_change_task_assign(self):
        response = self.client.patch(f"/tasks/{self.task_admin.pk}/assign/", data={'assigned_to': self.simple_user.id},
                                     **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Change task assign by task owner
    def test_owner_user_change_task_assign(self):
        response = self.client.patch(f"/tasks/{self.task_simple_user.pk}/assign/",
                                     data={'assigned_to': self.admin_user.id},
                                     **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Change task assign by simple user
    def test_simple_user_change_task_assign(self):
        response = self.client.patch(f"/tasks/{self.task_admin.pk}/assign/", data={'assigned_to': self.admin_user.id},
                                     **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Change task status by admin user
    def test_admin_user_change_task_status(self):
        response = self.client.patch(f"/tasks/{self.task_admin.pk}/complete/", data={'status': 'True'},
                                     **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Change task status by task owner
    def test_owner_user_change_task_status(self):
        response = self.client.patch(f"/tasks/{self.task_simple_user.pk}/complete/", data={'status': 'True'},
                                     **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Change task status by simple user
    def test_simple_user_change_task_status(self):
        response = self.client.patch(f"/tasks/{self.task_admin.pk}/complete/", data={'status': 'True'},
                                     **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentTestCase(APITestCase):
    def setUp(self):
        # Create simple user
        self.simple_user = User.objects.create(
            email='simple@test.com',
            first_name='simple_first_name',
            last_name='simple_last_name',
            username='simple@test.com',
            is_superuser=False,
            is_staff=False,
        )
        self.password = self.simple_user.set_password('simple')
        self.simple_user.save()

        # Create admin user
        self.admin_user = User.objects.create(
            email='admin@test.com',
            first_name='admin_first_name',
            last_name='admin_last_name',
            username='admin@test.com',
            is_superuser=True,
            is_staff=True,
        )
        self.password = self.admin_user.set_password('admin')
        self.admin_user.save()

        # Create task for admin user
        self.task_admin = Task.objects.create(
            title='admin_title',
            description='admin_description',
            status=False,
            assigned_to=self.admin_user
        )
        self.task_admin.save()

        # Create task for simple user
        self.task_simple_user = Task.objects.create(
            title='simple_title',
            description='simple_description',
            status=False,
            assigned_to=self.simple_user
        )
        self.task_simple_user.save()

        # Create comment by admin user
        self.comment_admin_user = Comment.objects.create(
            content='test_content',
            task=self.task_admin
        )

        # Create comment by simple user
        self.comment_simple_user = Comment.objects.create(
            content='test_content',
            task=self.task_simple_user
        )

    # Get all task comments by admin user
    def test_get_all_comments_by_admin_user(self):
        response = self.client.get(f"/tasks/{self.task_simple_user.pk}/comments/", **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Get all task comment by simple user
    def test_get_all_comments_by_simple_user(self):
        response = self.client.get(f"/tasks/{self.task_admin.pk}/comments/", **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Create task comment by admin user
    def test_create_task_comment_by_admin_user(self):
        response = self.client.post(f"/tasks/{self.task_admin.pk}/comments/", data={'content': 'test_content'},
                                    **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Create task comment by simple user
    def test_create_task_comment_by_simple_user(self):
        response = self.client.post(f"/tasks/{self.task_simple_user.pk}/comments/", data={'content': 'test_content'},
                                    **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TaskTimeLogTestCase(APITestCase):
    def setUp(self):
        # Create simple user
        self.simple_user = User.objects.create(
            email='simple@test.com',
            first_name='simple_first_name',
            last_name='simple_last_name',
            username='simple@test.com',
            is_superuser=False,
            is_staff=False,
        )
        self.password = self.simple_user.set_password('simple')
        self.simple_user.save()

        # Create admin user
        self.admin_user = User.objects.create(
            email='admin@test.com',
            first_name='admin_first_name',
            last_name='admin_last_name',
            username='admin@test.com',
            is_superuser=True,
            is_staff=True,
        )
        self.password = self.admin_user.set_password('admin')
        self.admin_user.save()

        # Create task for admin user
        self.task_admin = Task.objects.create(
            title='admin_title',
            description='admin_description',
            status=False,
            assigned_to=self.admin_user
        )
        self.task_admin.save()

        # Create task for simple user
        self.task_simple_user = Task.objects.create(
            title='simple_title',
            description='simple_description',
            status=False,
            assigned_to=self.simple_user
        )
        self.task_simple_user.save()

        # Create task time log by admin user
        self.task_time_log_admin_user = TimeLog.objects.create(
            task=self.task_admin,
            user=self.admin_user,
            started_at=timezone.now(),
            duration=None
        )

        # Create task time log by simple user
        self.task_time_log_simple_user = TimeLog.objects.create(
            task=self.task_simple_user,
            user=self.simple_user,
            started_at=timezone.now(),
            duration=None
        )

    # Get all task timelogs by id by admin user
    def test_get_all_task_timelogs_by_admin_user(self):
        response = self.client.get(f"/tasks/{self.task_admin.pk}/timelogs/", **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Get all task timelogs by id by simple user
    def test_get_all_task_timelogs_by_simple_user(self):
        response = self.client.get(f"/tasks/{self.task_simple_user.pk}/timelogs/", **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Create task timelog by admin user
    def test_create_task_timelogs_by_admin_user(self):
        response = self.client.post(f"/tasks/{self.task_admin.pk}/timelogs/",
                                    data={'minutes': 20, 'started_at': timezone.now()}, **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Create task timelog by simple user
    def test_create_task_timelogs_by_simple_user(self):
        response = self.client.post(f"/tasks/{self.task_simple_user.pk}/timelogs/",
                                    data={'minutes': 20, 'started_at': timezone.now()}, **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Start task timer by admin user
    def test_get_start_task_by_admin_user(self):
        response = self.client.get(f"/tasks/{self.task_admin.pk}/timelogs/start/", **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Start task timer by simple user
    def test_get_start_task_by_simple_user(self):
        response = self.client.get(f"/tasks/{self.task_admin.pk}/timelogs/start/", **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Stop task timer by admin user
    def test_get_end_task_by_admin_user(self):
        response = self.client.get(f"/tasks/{self.task_admin.pk}/timelogs/stop/", **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Stop task timer by simple user
    def test_get_end_task_by_simple_user(self):
        response = self.client.get(f"/tasks/{self.task_admin.pk}/timelogs/stop/", **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Get all timelogs by admin user
    def test_get_timelogs_by_admin_user(self):
        response = self.client.get('/timelogs/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Get all timelogs by simple user
    def test_get_timelogs_by_simple_user(self):
        response = self.client.get('/timelogs/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
