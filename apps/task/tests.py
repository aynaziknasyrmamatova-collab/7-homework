from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from .models import Task


class SimpleTaskCachingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="task-user",
            password="test-password",
        )
        cache.clear()
        self.task = Task.objects.create(
            title="Купить хлеб",
            description="Свежий батон"
        )

    def test_caching_flow(self):
        # 1. Первый запрос: кэш пустой, данные читаются из базы
        res1 = self.client.get("/task/")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res1.data), 1)

        # 2. Проверяем, что в кэше появились данные
        self.assertIsNotNone(cache.get("tasks"))

        # 3. Добавляем новую запись напрямую в базу
        Task.objects.create(title="Купить молоко", description="1 литр")

        # 4. Запрос через API по-прежнему возвращает 1 запись (из кэша)
        res2 = self.client.get("/task/")
        self.assertEqual(len(res2.data), 1)

        # 5. Делаем POST через API — кэш должен очиститься
        self.client.force_authenticate(user=self.user)
        post_res = self.client.post("/task/", {"title": "Купить масло", "description": "Пачка"}, format="json")
        self.assertEqual(post_res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(cache.get("tasks"))

        # 6. Следующий GET вернет уже все 3 актуальные записи
        res3 = self.client.get("/task/")
        self.assertEqual(len(res3.data), 3)

    def test_update_invalidates_cached_tasks(self):
        self.client.get("/task/")
        self.client.force_authenticate(user=self.user)

        response = self.client.put(
            f"/task/{self.task.id}/",
            {"title": "Купить муку", "description": "1 кг", "is_completed": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(cache.get("tasks"))

    def test_task_creation_requires_authentication_but_listing_is_public(self):
        listing = self.client.get("/task/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)

        response = self.client.post(
            "/task/",
            {"title": "Новая задача"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        authenticated_response = self.client.post(
            "/task/",
            {"title": "Новая задача"},
            format="json",
        )
        self.assertEqual(authenticated_response.status_code, status.HTTP_201_CREATED)

    def test_deadline_text_and_grouped_endpoint(self):
        deadline = timezone.now() + timedelta(days=2, hours=1)
        task = Task.objects.create(title="Подготовиться", deadline=deadline)

        list_response = self.client.get("/task/")
        task_data = next(item for item in list_response.data if item["id"] == task.id)
        self.assertTrue(task_data["time_left"].startswith("2 days left"))

        grouped_response = self.client.get("/task/grouped/")
        self.assertEqual(grouped_response.status_code, status.HTTP_200_OK)
        self.assertIn(deadline.date().isoformat(), grouped_response.data)
        self.assertEqual(grouped_response.data[deadline.date().isoformat()][0]["id"], task.id)

    def test_missing_and_expired_deadline_messages(self):
        expired = Task.objects.create(
            title="Старый дедлайн",
            deadline=timezone.now() - timedelta(days=1),
        )

        self.assertEqual(
            self.client.get(f"/task/{self.task.id}/").data["time_left"],
            "Дедлайн не указан",
        )
        self.assertEqual(
            self.client.get(f"/task/{expired.id}/").data["time_left"],
            "Дедлайн просрочен",
        )
