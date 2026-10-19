from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Shop(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shops',
        null=True,
        blank=True,
        verbose_name='Владелец'
    )
    name = models.CharField(max_length=60, verbose_name='Название')
    color = models.CharField(max_length=30, verbose_name='Цвет')
    logo = models.ImageField(upload_to='logo/', blank=True, null=True, verbose_name='Логотип')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")

    def __str__(self):
        return self.name


class Product(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='products',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
    )
    title = models.CharField(max_length=200, verbose_name="Название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена товара")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение товара")

    def __str__(self):
        return self.title
