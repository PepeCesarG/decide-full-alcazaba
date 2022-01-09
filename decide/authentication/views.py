from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

from .serializers import UserSerializer


class GetUserView(APIView):
    def post(self, request):
        
        if(request.data.get('token')!=None):
            key = request.data.get('token', '')
            tk = get_object_or_404(Token, key=key)
        
        else:
            if request.user.is_authenticated:
                user = request.user
        
        return Response(UserSerializer(tk.user, many=False).data)

class ProfileView(TemplateView):
    template_name="profile.html"
    def get_context_data(self):
        context=super().get_context_data()
        return context
        
class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)
        
        
class SigninView(TemplateView):
    template_name="signin.html"
    def get_context_data(self):
        context=super().get_context_data()
        return 
        
class LoginView(TemplateView):
    template_name="login.html"
    def get_context_data(self):
        context=super().get_context_data()
        return 
    
    
