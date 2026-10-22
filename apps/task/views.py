from collections import defaultdict
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from .models import Task
from .serializers import TaskSerializer


class TaskView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Получить список задач',
        description='Возвращает задачи; результат списка кэшируется на 60 секунд.',
        responses=TaskSerializer(many=True),
    )
    def get(self, request):
        # 1. Проверяем, есть ли данные в кэше
        tasks_data = cache.get("tasks")

        # Если данные есть в кэше — возвращаем их
        if tasks_data is not None:
            return Response(tasks_data)

        # 2. Если данных нет в кэше — берем из базы данных
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        tasks_data = serializer.data

        # 3. Сохраняем в кэш на 60 секунд
        cache.set("tasks", tasks_data, 60)

        return Response(tasks_data)

    @extend_schema(
        summary='Создать задачу',
        description='Создает задачу и очищает кэш списка. Требуется аутентификация.',
        request=TaskSerializer,
        responses={status.HTTP_201_CREATED: TaskSerializer},
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 4. Очищаем кэш при создании новой задачи
        cache.delete("tasks")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GroupedTaskView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Сгруппировать задачи по дедлайну',
        description='Возвращает задачи, сгруппированные по датам дедлайна.',
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        grouped_tasks = defaultdict(list)
        tasks = Task.objects.all().order_by("deadline")
        for task in tasks:
            date_key = task.deadline.date().isoformat() if task.deadline else "Без дедлайна"
            grouped_tasks[date_key].append(TaskSerializer(task).data)
        return Response(dict(grouped_tasks))


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(summary='Получить задачу', responses=TaskSerializer)
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @extend_schema(
        summary='Полностью обновить задачу',
        description='Заменяет поля задачи и очищает кэш списка. Требуется аутентификация.',
        request=TaskSerializer,
        responses=TaskSerializer,
    )
    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Очищаем кэш при обновлении задачи
        cache.delete("tasks")
        return Response(serializer.data)

    @extend_schema(
        summary='Удалить задачу',
        description='Удаляет задачу и очищает кэш списка. Требуется аутентификация.',
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()

        # Очищаем кэш при удалении задачи
        cache.delete("tasks")
        return Response({"message": "Задача удалена"}, status=status.HTTP_204_NO_CONTENT)
