from django.shortcuts import render, redirect
from django.utils import translation

def homepage(request):
    return render(request, 'homepage.html', {})

def guia(request):
    return render(request, 'guia.html', {})

