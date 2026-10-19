from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время окончания срока")
    is_completed = models.BooleanField(default=False, verbose_name="Статус выполнения")
    def __str__(self):
        return self.title
