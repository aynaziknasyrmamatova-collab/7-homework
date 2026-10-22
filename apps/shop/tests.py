from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import Category, Product, Shop


class ProductApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.admin = User.objects.create_user(
			username="shop-admin",
			password="test-password",
			is_staff=True,
		)
		self.client.force_authenticate(user=self.admin)
		self.shop = Shop.objects.create(name="Market", color="green")
		self.category = Category.objects.create(name="Books")

	def test_product_create_and_filters(self):
		response = self.client.post(
			"/shop/products/",
			{
				"shop": self.shop.id,
				"category": self.category.id,
				"title": "Novel",
				"price": "15.00",
				"stock": 3,
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		filtered = self.client.get(
			"/shop/products/",
			{"price": "15.00", "category": self.category.id, "shop": self.shop.id},
		)
		self.assertEqual(filtered.status_code, 200)
		self.assertEqual(filtered.data["count"], 1)

	def test_category_endpoint_lists_categories(self):
		response = self.client.get("/shop/categories/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["results"][0]["name"], "Books")

	def test_product_creation_requires_staff(self):
		anonymous_client = APIClient()
		response = anonymous_client.post(
			"/shop/products/",
			{
				"shop": self.shop.id,
				"category": self.category.id,
				"title": "Novel",
				"price": "15.00",
				"stock": 3,
			},
			format="json",
		)
		self.assertEqual(response.status_code, 401)
