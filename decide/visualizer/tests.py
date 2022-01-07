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

import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


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



class TestShowgraphics(BaseTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        super().setUp()
        
    def tearDown(self):
        self.driver.quit()
        super().tearDown()
    
    def test_showgraphics(self):
        self.driver.get("http://localhost:8000/")
        self.driver.set_window_size(1848, 1016)
        self.driver.find_element(By.LINK_TEXT, "Color de pelo").click()
        self.driver.find_element(By.LINK_TEXT, "Ver Gráficas").click()
        url = self.driver.current_url
        assert url == "http://localhost:8000/visualizer/3/graficos"
    
    def test_showgraphics_title_ok(self):
        self.driver.get("http://localhost:8000/")
        self.driver.set_window_size(1848, 1016)
        self.driver.find_element(By.LINK_TEXT, "Color de pelo").click()
        self.driver.find_element(By.LINK_TEXT, "Ver Gráficas").click()
        assert self.driver.find_element(By.CSS_SELECTOR, "h1").text == "GRÁFICOS DE LA VOTACIÓN"

    def test_showgraphics_allgraphics_ok(self):
        self.driver.get("http://localhost:8000/")
        self.driver.set_window_size(1848, 1016)
        self.driver.find_element(By.LINK_TEXT, "Color de pelo").click()
        self.driver.find_element(By.LINK_TEXT, "Ver Gráficas").click()
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".col-lg-12")
        assert len(elements) > 0
    
    def test_showgraphics_footer_ok(self):
        self.driver.get("http://localhost:8000/")
        self.driver.set_window_size(1848, 1016)
        self.driver.find_element(By.LINK_TEXT, "Color de pelo").click()
        self.driver.find_element(By.LINK_TEXT, "Ver Gráficas").click()
        element = self.driver.find_elements(By.CSS_SELECTOR, ".footer-content")
        assert len(element) > 0
        assert self.driver.find_element(By.CSS_SELECTOR, "h3").text == "Decide"
