from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)
from voting.models import Voting
from django.contrib.auth.models import User
from base.perms import UserIsStaff
from .models import Census


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        votings = request.data.get('votings')
        voters = request.data.get('voters')
        try:
            census = Census(name = name)
            census.save()
            for voting_id in votings:
                census.voting_ids.add(Voting.objects.get(pk=voting_id))
            for voter_id in voters:
                census.voter_ids.add(Voter.objects.get(pk=voter_id))
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_ids__id=voting_id).values_list('voter_ids', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        name = request.data
        census = Census.objects.filter(name=name)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        print('EL votante a comparar es:' +voter)  
        print("La votacion es " + str(voting_id))
        censuss = Census.objects.all()
        for c in censuss:
            print("Se esta mirando el censo " + c.name)
            voters = c.voter_ids.all()
            votings = c.voting_ids.all()
            print("Los votantes permitidos son " + str(voters.values_list('id', flat=True)))
            print("Las votaciones que incluye son " + str(votings.values_list('id', flat=True)))              
            if(any(person.user.id == int(voter) for person in voters) and any(voting.id == voting_id for voting in votings)):
                print("El votante es valido")
                return Response('Valid voter')
        return Response('Invalid voter', status=ST_401)
