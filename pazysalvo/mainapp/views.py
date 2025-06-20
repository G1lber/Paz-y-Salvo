from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request, 'index.html')

def custom_login(request):
    return render(request, 'login.html')

def pazysalvo(request):
    return render(request, 'pazysalvo.html')

def inicio(request):
    return render(request, 'dashboard.html')

def aprendices(request):
    return render(request, 'aprendices.html')

def prestarlibro(request):
    return render(request, 'prestarlibro.html')

def pendientes(request):
    return render(request, 'pendientes.html')