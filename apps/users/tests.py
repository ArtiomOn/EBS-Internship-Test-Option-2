from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

User = get_user_model()


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        "HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'
    }


class UserTestCase(APITestCase):

    def setUp(self):
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

        self.refresh = RefreshToken.for_user(self.admin_user)

    def test_user_access_token(self):
        response = self.client.post('/token/', data={'email': self.admin_user.email, 'password': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_refresh_token(self):
        response = self.client.post('/token/refresh/', data={'refresh': str(self.refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list(self):
        response = self.client.get('/users/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_list(self):
        response = self.client.get('/users/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_register(self):
        response = self.client.post(path='/users/register/', data={
            "first_name": 'admin_first_name',
            "last_name": 'admin_last_name',
            "email": "admin@example.com",
            "password": 'admin_password'},
                                    **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_register(self):
        response = self.client.post(path='/users/register/', data={
            "first_name": 'simple_first_name',
            "last_name": 'simple_last_name',
            "email": "simple@example.com",
            "password": 'simple_password'},
                                    **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
