from django.contrib.auth import login, logout
from rest_framework import serializers, status, permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, inline_serializer

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Регистрация пользователя',
        description='Создает учетную запись по имени пользователя, email и паролю с подтверждением.',
        request=RegisterSerializer,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name='RegisterResponse',
                fields={
                    'message': serializers.CharField(),
                    'user': UserSerializer(),
                },
            ),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Пользователь успешно зарегистрирован",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Вход и получение токенов',
        description=(
            'Принимает username и password. Возвращает данные пользователя, '
            'Django Token для заголовка Authorization: Token и пару JWT '
            '(access/refresh) для Authorization: Bearer.'
        ),
        request=LoginSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='LoginResponse',
                fields={
                    'message': serializers.CharField(),
                    'user': UserSerializer(),
                    'token': serializers.CharField(),
                    'access': serializers.CharField(),
                    'refresh': serializers.CharField(),
                },
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        django_token, _ = Token.objects.get_or_create(user=user)
        jwt_refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": f"Вы успешно вошли в систему, {user.username}",
                "user": UserSerializer(user).data,
                "token": django_token.key,
                "access": str(jwt_refresh.access_token),
                "refresh": str(jwt_refresh),
            },
            status=status.HTTP_200_OK
        )

class LogOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Выход и отзыв Django Token/JWT refresh',
        description=(
            'Удаляет Django Token и завершает сессию. Если передан собственный '
            'JWT refresh в теле запроса, он добавляется в blacklist. Уже выданный '
            'JWT access остается действительным до истечения срока действия.'
        ),
        request=LogoutSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='LogoutResponse',
                fields={'message': serializers.CharField()},
            ),
        },
    )
    def post(self, request):
        user = request.user
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data.get('refresh')
        if refresh:
            try:
                refresh_token = RefreshToken(refresh)
            except TokenError as error:
                raise serializers.ValidationError(
                    {'refresh': 'Недействительный или просроченный JWT refresh-токен.'}
                ) from error
            if str(refresh_token.get('user_id')) != str(user.pk):
                raise serializers.ValidationError(
                    {'refresh': 'Можно отозвать только собственный JWT refresh-токен.'}
                )
            refresh_token.blacklist()
        Token.objects.filter(user=user).delete()
        logout(request)
        return Response(
            {
                "message": "Вы успешно вышли из аккаунта",
            },
            status=status.HTTP_200_OK
        )

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Получить профиль текущего пользователя',
        responses=UserSerializer,
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Полностью обновить профиль текущего пользователя',
        request=UserSerializer,
        responses=UserSerializer,
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Частично обновить профиль текущего пользователя',
        request=UserSerializer,
        responses=UserSerializer,
    )
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DjangoTokenObtainView(ObtainAuthToken):
    @extend_schema(
        summary='Получить Django Token',
        description='Обменивает имя пользователя и пароль на Django Token.',
        request=AuthTokenSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='DjangoTokenResponse',
                fields={'token': serializers.CharField()},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class JWTTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        summary='Получить JWT-токены',
        description='Обменивает имя пользователя и пароль на пару JWT access/refresh.',
        request=TokenObtainPairSerializer,
        responses=TokenObtainPairSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class JWTTokenRefreshView(TokenRefreshView):
    @extend_schema(
        summary='Обновить JWT access-токен',
        description='Принимает действующий refresh-токен и возвращает новый access-токен.',
        request=TokenRefreshSerializer,
        responses=TokenRefreshSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)