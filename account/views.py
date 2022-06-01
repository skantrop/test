from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, ActivationSerializer, LoginSerializer, ForgotPasswordSerializer, \
    CreateNewPasswordSerializer, ChangePasswordSerializer

'''
1. Регистрация 
2. Активация
3. Логин
4. Восстановление пароля
5. Смена пароля
6. Профиль пользователя
'''


class RegistrarionView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Your account successfully registered', status=status.HTTP_201_CREATED)


class ActivationView(APIView):
    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate()
            return Response('Your account is successfully activated', status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response('You are successfully logged out', status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer
        if serializer.is_valid(raise_exception=True):
            serializer.send_reset_email()
            return Response('Code for password restore was sent to your email', status=status.HTTP_200_OK)


class ResetPasswordCompleteView(APIView):
    def post(self, request):
        serializer = CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.create_pass()
            return Response('Password was restored successfully', status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Password changes successfully!', status=status.HTTP_200_OK)


class UserProfileView(APIView):
    pass

