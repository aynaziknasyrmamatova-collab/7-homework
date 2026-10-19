from rest_framework import serializers
from .models import Shop, Product, Category

class ShopSer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Shop
        fields = ('id', 'name', 'color', 'logo', 'user')
        read_only_fields = ('id', 'user')
class ProductSer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'shop', 'category', 'title', 'price', 'stock', 'image')
        read_only_fields = ('id',)


class CategorySer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)
        