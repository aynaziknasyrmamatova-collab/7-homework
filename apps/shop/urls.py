from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ShopViewSets, ProductViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'shop', ShopViewSets, basename='shop')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls))
]

