from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Shop,Category,Product
from .serializer import ShopSer,ProductSer,CategorySer
from .pagination import ShopPagination,ProductPagination,CategoryPagination
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary='Список магазинов',
        description='Возвращает магазины с фильтрацией по имени и цвету, поиском и сортировкой.',
    ),
    retrieve=extend_schema(summary='Детали магазина'),
    create=extend_schema(
        summary='Создать магазин',
        description='Создает магазин для текущего пользователя. Требуется аутентификация.',
    ),
    update=extend_schema(summary='Полностью обновить магазин владельца'),
    partial_update=extend_schema(summary='Частично обновить магазин владельца'),
    destroy=extend_schema(summary='Удалить магазин владельца'),
)
class ShopViewSets(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSer
    pagination_class = ShopPagination
    permission_classes = [IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'color']
    search_fields = ['name', 'color']
    ordering_fields = ['name', 'id']
    ordering = ['id']

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

@extend_schema_view(
    list=extend_schema(
        summary='Список товаров',
        description='Поддерживает фильтр по цене, категории и магазину, поиск по названию и сортировку.',
    ),
    retrieve=extend_schema(summary='Детали товара'),
    create=extend_schema(
        summary='Создать товар',
        description='Создает товар. Требуются права администратора (is_staff).',
    ),
    update=extend_schema(summary='Полностью обновить товар администратора'),
    partial_update=extend_schema(summary='Частично обновить товар администратора'),
    destroy=extend_schema(summary='Удалить товар администратора'),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('shop', 'category').all()
    serializer_class = ProductSer
    pagination_class = ProductPagination
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'category', 'shop']
    search_fields = ['title']
    ordering_fields = ['price', 'title']
    ordering = ['id']

@extend_schema_view(
    list=extend_schema(
        summary='Список категорий',
        description='Поддерживает поиск по названию и описанию, а также сортировку.',
    ),
    retrieve=extend_schema(summary='Детали категории'),
    create=extend_schema(
        summary='Создать категорию',
        description='Создает категорию. Требуются права администратора (is_staff).',
    ),
    update=extend_schema(summary='Полностью обновить категорию администратора'),
    partial_update=extend_schema(summary='Частично обновить категорию администратора'),
    destroy=extend_schema(summary='Удалить категорию администратора'),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySer
    pagination_class = CategoryPagination
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['id']
