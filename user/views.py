from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from .models import User
from .serializer import UserCreateSerializer


# Create your views here.

class UserRegistrationView(CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

