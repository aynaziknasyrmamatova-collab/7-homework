from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Books, Library
from .serializers import BooksSerializer, LibrarySerializer


class BookListApi(APIView):
    def get(self, request):
        books = Books.objects.all()
        serializer = BooksSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BooksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LibraryListApi(APIView):
    def get(self, request):
        libraries = Library.objects.prefetch_related("books")
        serializer = LibrarySerializer(libraries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LibrarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
