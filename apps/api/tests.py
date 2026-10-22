from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class APIDocumentationTests(TestCase):
    def test_swagger_ui_and_schema_are_available(self):
        client = APIClient()

        swagger_response = client.get('/api/docs/')
        self.assertEqual(swagger_response.status_code, status.HTTP_200_OK)

        schema_response = client.get('/api/schema/')
        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
        self.assertIn('/users/login/', schema_response.data['paths'])
        self.assertIn('/shop/products/', schema_response.data['paths'])
        self.assertIn('/api/auth/jwt/create/', schema_response.data['paths'])
        self.assertIn('/api/auth/token/', schema_response.data['paths'])
