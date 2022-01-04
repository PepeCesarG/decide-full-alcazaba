import logging
import os
import random

from base import mods
from base.tests import BaseTestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.test import TestCase
from mixnet.models import Auth
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from voting.models import Question, QuestionOption, Voting
from django.core.files.uploadedfile import SimpleUploadedFile

from .admin import CensusAdmin, VoterAdmin
from .models import Census, Voter


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
        '''
    #TEST QUE COMPRUEBA LA FEATURE #34 PARA EL CENSO: Automatizar el proceso de creacion de votos
    #de tal manera que si se crea un votante con una localidad, edad y genero se creen los censos 
    #respectivos, para hacer este test es necesario que se introduzca un usuario con permisos y tener 
    #la base de datos limpia
    def test_create_check_censuss(self):
        usuarioconpermisos = ''
        contraseñaconpermisos = ''
        if usuarioconpermisos=='' or contraseñaconpermisos=='':
            logging.debug('NO SE HA INTRODUCIDO USUARIO O CONTRASEÑA EN EL TEST')
        i = random.randint(0,100000)
        logger = logging.getLogger('selenium.webdriver.remote.remote_connection') 
        logger.setLevel(logging.WARNING)
        options = webdriver.ChromeOptions()
        options.headless = False
        driver = webdriver.Chrome(options=options)
        driver.get("http://127.0.0.1:8081/admin")
        username = driver.find_element_by_name('username')
        password = driver.find_element_by_name('password')
        username.send_keys(usuarioconpermisos)
        password.send_keys(contraseñaconpermisos)
        driver.find_element_by_id("login-form").submit()
        #driver.get('http://>>>>>>> develop127.0.0.1:8081/admin/auth/user/')
        driver.get("http://127.0.0.1:8081/admin/auth/user/add/")
        createuser = driver.find_element_by_name('username')
        createpassword = driver.find_element_by_name('password1')
        confirmpassword = driver.find_element_by_name('password2')
        createuser.send_keys('usuarioprueba'+str(i))
        createpassword.send_keys('contrasenaprueba1')
        confirmpassword.send_keys('contrasenaprueba1')
        driver.find_element_by_id('user_form').submit()
        driver.get("http://127.0.0.1:8081/admin/census/voter/add")
        selectuser = Select(driver.find_element_by_name('user'))
        selectuser.select_by_visible_text('usuarioprueba'+str(i))
        selectlocation = Select(driver.find_element_by_name('location'))
        selectlocation.select_by_visible_text('Zaragoza')
        insertedad = driver.find_element_by_name('edad')
        insertedad.send_keys('45')
        selectgenero = Select(driver.find_element_by_name('genero'))
        selectgenero.select_by_visible_text('Hombre')
        driver.find_element_by_id('voter_form').submit()
        driver.get('http://127.0.0.1:8081/admin/census/census/')
        censocreadoporgenero = driver.find_element_by_link_text('Hombre').text
        censocreadoporlocation =driver.find_element_by_link_text('Sevilla').text
        censocreadoporedad = driver.find_element_by_link_text('45').text
        logging.debug('Censo por locacion:' + str(censocreadoporlocation))
        logging.debug('Censo por genero:' + str(censocreadoporgenero))
        logging.debug('Censo por edad:' + str(censocreadoporedad))
        '''
    def create_voter(self):
        Voter.objects.all().delete()
        self.user, _ = User.objects.get_or_create(username='testvoter{}'.format(1))
        self.user.is_active = True
        self.user.save()
        self.voter, _ = Voter.objects.get_or_create(user=self.user, location='Avila', edad='50',genero='Mujer')
        self.voter.save()
    def create_census(self):
        Census.objects.all().delete()
        Voting.objects.all().delete()
        self.voting = self.create_voting()
        self.voting.save()
        self.create_voter()
        self.census = Census(name="Avila")
        self.census.id = 1
        self.census.save()
        self.census.voting_ids.add(self.voting)
        self.census.save()
        self.census.voter_ids.add(self.voter)
        self.census.save()
        self.census = Census(name="50")
        self.census.id = 2
        self.census.save()
        self.census.voting_ids.add(self.voting)
        self.census.save()
        self.census.voter_ids.add(self.voter)
        self.census.save()
        self.census = Census(name="Mujer")
        self.census.id = 3
        self.census.save()
        self.census.voting_ids.add(self.voting)
        self.census.save()
        self.census.voter_ids.add(self.voter)
        self.census.save()

            
    def test_check_vote_permissions(self):
        self.create_census()
        response = self.client.get('/census/{}/?voter_id={}'.format(self.voting.id, 580), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')
        response = self.client.get('/census/{}/?voter_id={}'.format(self.voting.id, self.voter.user.id), format='json')
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
        self.assertEqual(response.json(), {'voters': [self.voter.id,self.voter.id,self.voter.id]})
    
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
    def test_add_new_voters(self):
        self.create_census()
        print('El voter a añadir es:'+ str(self.voter.id))
        print('El voting a añadir es:'+ str(self.voting.id))
        data = {'name':'prueba creacion','votings': [self.voting.id], 'voters': [self.voter.id]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login(user='admin',password='qwerty')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)
    
    '''
    
    def test_destroy_voter(self):
        self.create_census()
        
        data = 'test census'
        for c in Census.objects.all():
            response = self.client.delete('/census/{}/'.format(c.id), data, format='json')
            self.assertEqual(response.status_code, 204)

    def test_csv_import_success(self):
        self.login()
        self.create_census()
        data = open('./census/test_csv/positive.csv', 'rb')
        data = SimpleUploadedFile(content = data.read(), name = data.name, content_type='multipart/form-data')
        
        response = self.client.post('/census/import-csv/', {"csv_file": data}, format="multipart")
        data.close()
        logging.debug("Test CSV exit code: {}".format(response.status_code))
        logging.debug(response.json())
            
    ''' 
    def test_csv_import_success(self):
        self.login()
        self.create_census()
        with open('./census/test_csv/positive.csv') as f:  
            data = {
                "name" : "csv_test",
                "csv_file" : f
            }
            response = self.client.post('/census/import-csv/', data, content_type='application/json')
        logging.debug("Test CSV exit code: {}".format(response.status_code))
        logging.debug(response.json())

    
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
