from django.shortcuts import render, redirect
from django.utils import translation
from voting.models import Voting

def homepage(request):
    votingsList  = list(Voting.objects.all())
    votings = {}
    for voting in votingsList:
        votings[voting.id] = {
                'id': voting.id,
                'name': voting.name,
            }
    return render(request, 'homepage.html', {"votings":votings.values()})

def guia(request):
    return render(request, 'guia.html', {})

