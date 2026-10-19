from django.test import TestCase
from rest_framework.test import APIClient

from .models import Books, Library


class LibraryApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_library_list_includes_books_and_delete_cascades(self):
		library = Library.objects.create(name="Central", address="Main street", city="London")
		book = Books.objects.create(
			library=library,
			title="A book",
			author="An author",
			price="12.50",
		)

		response = self.client.get("/books/libraries/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data[0]["books"][0]["id"], book.id)

		library.delete()
		self.assertFalse(Books.objects.filter(pk=book.pk).exists())
