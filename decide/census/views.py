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
            for voting in votings:
                census.votings_id.add(voting)
            for voter in voters:
                census.voters_id.add(voter)
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(votings_id__id=voting_id).values_list('voters_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        name = request.data.get('name')
        census = Census.objects.filter(name=name)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        print("La votacion es " + str(voting_id) + " y el votante es " + voter)
        censuss = Census.objects.all()
        for c in censuss:
            print("Se esta mirando el censo " + c.name)
            voters = c.voter_ids.all()
            votings = c.voting_ids.all()
            print("Los votantes permitidos son " + str(voters))
            print("Las votaciones que incluye son " + str(votings))            
                
            if(any(person.id == int(voter) for person in voters) and any(voting.id == voting_id for voting in votings)):
                print("El votante es valido")
                return Response('Valid voter')
            else:
                return Response('Invalid voter', status=ST_401)
