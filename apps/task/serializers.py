from django.utils import timezone
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    time_left = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ("id", "title", "description", "deadline", "is_completed", "time_left")
        read_only_fields = ("id",)

    def get_time_left(self, task):
        if task.deadline is None:
            return "Дедлайн не указан"

        remaining = task.deadline - timezone.now()
        if remaining.total_seconds() <= 0:
            return "Дедлайн просрочен"

        days = remaining.days
        if days:
            return f"{days} {'day' if days == 1 else 'days'} left"
        hours = remaining.seconds // 3600
        if hours:
            return f"{hours} {'hour' if hours == 1 else 'hours'} left"
        return "Less than an hour left"

    # Валидация поля title
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Минимум 3 символа в названии!")
        return value.strip()
