import random
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.contrib.auth.models import User
from base import mods
from base.tests import BaseTestCase
from .models import Voter
from .admin import CensusAdmin, VoterAdmin
from django.core.exceptions import ObjectDoesNotExist
import os


class CensusTestCase(BaseTestCase):
    
    voter = None
    voting = None
    census = None
    
    def setUp(self):
        super().setUp()
        
    def tearDown(self):
        super().tearDown()
        self.census = None
        self.voting = None
        self.voter = None
        
    def create_voting(self):
        return self.create_voting_by_id(1)

    def create_voting_by_id(self, pk):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.id = pk
        return v
    
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.id = pk
        user.save()
        return user
    
    def test_create_check_censuss(self):
        self.voting = self.create_voting()
        self.voting.save()
        try:
            self.user = User.objects.get(username='testvoter{}'.format(1))
        except ObjectDoesNotExist:
            self.user = User.objects.create(username='testvoter{}'.format(1))
        self.user.is_active = True
        self.user.save()
        try:
            self.voter = Voter.objects.get(user=self.user)
        except ObjectDoesNotExist:
            self.voter = Voter.objects.create(user=self.user, location='Sevilla', edad='45',genero='Hombre')
        self.voter.save()
        self.censuss = Census.objects.all()
        i =1
        for self.c in self.censuss:
            if i == 1:
                self.assertEqual(self.c.name, 'Sevilla')
            if i==2:
                self.assertEqual(self.c.name, '45')
            if i==3:
                self.assertEqual(self.c.name,'Hombre')
            i = i +1
        return self.censuss
            

    '''
    def test_check_vote_permissions(self):
        self.censuss = self.test_create_check_censuss()
        self.census = self.censuss.objects.filter(name='Sevilla')
        response = self.client.get('/census/{}/?voter_id={}'.format(self.voting.id, self.voting.id), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(self.voting.id, self.voter.id), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        self.create_census()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [self.voter.id]})

    def test_add_new_voters_conflict(self):
        self.create_census()
        data = {'name': 'prueba creacion', 'votings': [self.voting.id], 'voters': [self.voter.id]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)
    '''
    '''def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)'''
    '''
    def test_destroy_voter(self):
        self.create_census()
        data = 'test census'
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())
    '''
    '''
    def test_csv_import_success(self):
        self.login()
        for i in range(1,5):
            self.create_voting_by_id(i)
            self.get_or_create_user(i)
        with open('./census/test_csv/positive.csv') as f:  
            data = {
                "nametest" : "csv_file",
                "file_data" : f
            }
            response = self.client.post('/census/import-csv/', data, format = 'json')
            print(response.status_code)
            self.assertEqual(3, Census.objects.count())
    '''