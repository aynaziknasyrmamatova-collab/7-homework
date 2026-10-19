from django.urls import path

from .views import BookListApi, LibraryListApi

urlpatterns = [
    path('books/', BookListApi.as_view()),
    path('libraries/', LibraryListApi.as_view()),
]
