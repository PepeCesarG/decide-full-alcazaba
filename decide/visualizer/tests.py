import random
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from django.db import transaction

from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.contrib.auth.models import User
from base import mods
from base.tests import BaseTestCase

import os


class VisualizerTestCase(BaseTestCase):
    
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
        v = Voting(name='test voting {}'.format(pk), question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.id = 1
        return v
    
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.id = pk
        user.save()
        return user
    

    def test_enpoint_is_avaliable(self):
        self.create_voting()
        response = self.client.get('/visualizer/all', format='json')
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.json(), {'voters': [self.voter.id]})

    def test_there_is_one_voting(self):
        self.create_voting()
        response = self.client.get('/visualizer/all', format='json')
        n = len(response.json())
        self.assertEqual(n, 1)

    def test_information_is_correct(self):
        self.create_voting()
        voting = self.create_voting()
        response = self.client.get('/visualizer/all', format='json')
        voting_id = voting.id
        voting_name = voting.name
        name_response = response.json()['2']['name']
        self.assertEqual(name_response, voting_name)
        voting_desc = voting.desc
        desc_response = response.json()['2']['description']
        self.assertEqual(desc_response, voting_desc)
        question_desc = str(voting.question).split(':')[0]
        question_desc_response = response.json()['2']['question_desc']
        self.assertEqual(question_desc, question_desc_response)
