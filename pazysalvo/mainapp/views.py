from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages

# Create your views here.
def custom_login(request):
    return render(request, 'login.html')

def pazysalvo(request):
    return render(request, 'pazysalvo.html')