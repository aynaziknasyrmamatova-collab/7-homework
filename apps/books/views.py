from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema

from .models import Books, Library
from .serializers import BooksSerializer, LibrarySerializer


class BookListApi(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(summary='Список книг', responses=BooksSerializer(many=True))
    def get(self, request):
        books = Books.objects.all()
        serializer = BooksSerializer(books, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Добавить книгу',
        description='Добавляет книгу в каталог. Требуется аутентификация.',
        request=BooksSerializer,
        responses={status.HTTP_201_CREATED: BooksSerializer},
    )
    def post(self, request):
        serializer = BooksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LibraryListApi(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(summary='Список библиотек', responses=LibrarySerializer(many=True))
    def get(self, request):
        libraries = Library.objects.prefetch_related("books")
        serializer = LibrarySerializer(libraries, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Добавить библиотеку',
        description='Создает библиотеку. Требуется аутентификация.',
        request=LibrarySerializer,
        responses={status.HTTP_201_CREATED: LibrarySerializer},
    )
    def post(self, request):
        serializer = LibrarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
