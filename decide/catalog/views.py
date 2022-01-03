from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html', {})

def guia(request):
    return render(request, 'guia.html', {})

