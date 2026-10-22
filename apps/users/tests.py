from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')

        self.user_password = 'StrongPassword123'
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password=self.user_password
        )

    def test_register_success(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePassword456',
            'password2': 'SecurePassword456'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        data = {
            'username': 'newuser2',
            'password': 'Password123',
            'password2': 'DifferentPassword456'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_register_short_password(self):
        data = {
            'username': 'newuser3',
            'password': '123',
            'password2': '123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_success(self):
        data = {
            'username': 'existinguser',
            'password': self.user_password
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'existinguser')
        self.assertTrue(response.data['token'])
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])

    def test_login_tokens_authenticate_with_django_token_and_jwt(self):
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'existinguser',
                'password': self.user_password,
            },
            format='json',
        )

        token_client = APIClient()
        token_client.credentials(
            HTTP_AUTHORIZATION=f"Token {login_response.data['token']}"
        )
        self.assertEqual(
            token_client.get(self.profile_url).status_code,
            status.HTTP_200_OK,
        )

        jwt_client = APIClient()
        jwt_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )
        self.assertEqual(
            jwt_client.get(self.profile_url).status_code,
            status.HTTP_200_OK,
        )

    def test_standalone_token_endpoints(self):
        credentials = {
            'username': 'existinguser',
            'password': self.user_password,
        }
        django_token_response = self.client.post(
            '/api/auth/token/',
            credentials,
            format='json',
        )
        self.assertEqual(django_token_response.status_code, status.HTTP_200_OK)
        self.assertTrue(django_token_response.data['token'])

        jwt_response = self.client.post(
            '/api/auth/jwt/create/',
            credentials,
            format='json',
        )
        self.assertEqual(jwt_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', jwt_response.data)
        self.assertIn('refresh', jwt_response.data)

        refresh_response = self.client.post(
            '/api/auth/jwt/refresh/',
            {'refresh': jwt_response.data['refresh']},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'existinguser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_unauthorized(self):
        response = self.client.get(self.profile_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_profile_authorized_and_patch(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')

        patch_data = {'email': 'updated@example.com'}
        patch_res = self.client.patch(self.profile_url, patch_data, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_logout(self):
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'existinguser',
                'password': self.user_password,
            },
            format='json',
        )
        token_client = APIClient()
        token_client.credentials(
            HTTP_AUTHORIZATION=f"Token {login_response.data['token']}"
        )
        response = token_client.post(
            self.logout_url,
            {'refresh': login_response.data['refresh']},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            token_client.get(self.profile_url).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        token_client.credentials()
        refresh_response = token_client.post(
            '/api/auth/jwt/refresh/',
            {'refresh': login_response.data['refresh']},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
