from django.shortcuts import render, redirect
from django.utils import translation

def homepage(request):
    return render(request, 'homepage.html', {})

def translate(request):
    user_language = user.profile.language
    translation.activate(user_language)
    request.session['django_language'] = user_language
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return redirect('/')