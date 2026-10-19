from django.db import models

# Create your models here.
class Library(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название библиотеки")
    address = models.CharField(max_length=255, verbose_name="Адрес библиотеки")
    city = models.CharField(max_length=100, verbose_name="Город")

    def __str__(self):
        return self.name


class Books(models.Model):
    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        related_name="books",
        null=True,
        blank=True,
        verbose_name="Библиотека",
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
