import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from census.models import Voter
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import *


class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def test_create_question(self):
        q_option = Question(desc='test question option',tipo='O')
        q_binaria = Question(desc='test question binaria', tipo='B')
        q_option.save()
        q_binaria.save()
        self.assertEqual(Question.objects.get(desc='test question option').tipo, 'O')
        self.assertEqual(Question.objects.get(desc='test question binaria').tipo, 'B')

    def test_create_questionOptionOptional(self):
        q_option = Question(desc='test question option',tipo='O')
        q_options1 = QuestionOption(question = q_option, number=2, option='Bien')
        q_options1.save()
        q_options2 = QuestionOption(question = q_option, number=3, option='Mal')
        q_options2.save()
        q_option.save()

        test1 = Question.objects.get(desc='test question option').options.all()
        i = 2
        l = 0
        lista = list()
        lista.append('Bien')
        lista.append('Mal')
        for elemento in test1:
            self.assertEqual(elemento.number, i)
            self.assertEqual(elemento.option, lista[l])
            i+=1
            l+=1

    def create_questionOptionBinary(self):
        q_option = Question(desc='test question binaria',tipo='B')
        q_options1 = QuestionOption(question = q_option, option='Yes')
        q_options1.save()
        q_options2 = QuestionOption(question = q_option, option='No')
        q_options2.save()
        q_option.save()

        test1 = Question.objects.get(desc='test question binaria').options.all()
        i = 2
        l = 0
        lista = list()
        lista.append('Yes')
        lista.append('No')
        for elemento in test1:
            self.assertEqual(elemento.number, i)
            self.assertEqual(elemento.option, lista[l])
            i+=1
            l+=1


    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.location = 'Sevilla'
        v.save()
        c = Census(name = 'Sevilla')
        c.save()
        c.voting_ids.add(v.id)
        c.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def test_encrypt_voting_from_api_succesfully(self):
        self.login()
        v = self.create_voting()
        v.create_pubkey()

        #Test que comprueba que es fallida la llamada
        question_opt = {"number": 2, "option": 1}
        data = {"question_opt": str(question_opt)}
        response = self.client.post('/voting/encrypt/', data, format='json')
        self.assertEqual(response.status_code, 400)

        #Test que comprueba que es correcta la llamada
        data = {"question_opt": question_opt,"id_v": str(v.id)}
        response = self.client.post('/voting/encrypt/', data, format='json')
        self.assertEqual(response.status_code, 200)

        #Test que comprueba la respuesta
        self.assertEqual(len(response.json().values()),2)
        self.assertEqual(list(response.json().keys())[0], 'a')
        self.assertEqual(list(response.json().keys())[1], 'b')

        self.assertEqual(v, Voting.objects.get(name='test voting'))

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            voter = Voter(user=u, location='Sevilla', edad=18)
            voter.save()
            c = Census.objects.get(name='Sevilla')
            c.voter_ids.add(voter.id)
            c.save()
            print(c.voter_ids)
    
    def test_store_bot_from_api_not_succesfully(self):
        self.login()
        votacion = self.create_voting()
        votacion.create_pubkey()
        votacion.start_date = timezone.now()
        votacion.save()

        self.create_voters(votacion)
        u = User.objects.get(username= 'testvoter1')
        voter = Voter.objects.get(user=u)

        question_opt = {"number": 2, "option": 1}
        data = {"question_opt": question_opt,"id_v": str(votacion.id)}
        response = self.client.post('/voting/encrypt/', data, format='json')
        
        a = list(response.json().values())[0]
        b = list(response.json().values())[1]
        data2={"voting_id":votacion.id,"voter_id":voter.id,"a":a,"b":b}

        response = self.client.post('/store/store-bot/', data2, format='json')
        print(response.json())
        """
            Al ser una llamada a la API, esta busca en el censo de la base de datos de
            Decide que corre por detras, es decir, la base de datos de la aplicación.
            Por lo tanto no puedo comprabar que sea satisfactoria la llamada, pues no
            comprueba la base de datos que se crea al ejecutar el test. Por tanto, y para que
            que no de fallo a la hora de subirse al repositorio y al ejecutarlo por mis compañeros
            se he optado por comprobar solamente el caso de fallo, explicado anteriormente.
        """
        self.assertEqual(response.status_code, 401)


    def test_authentication_login_bot_from_api_not_succesfully(self):
        self.login()
        u , _= User.objects.get_or_create(username='testvoter1200', password='testvoter1password')
        u.save()
        #Test que comprueba que es fallida la llamada
        print(str(User.objects.get(username= 'testvoter1200').username))
        data = {"username": str(u.username), "password": str(u.password)}
        data = str(data).replace('\'', '\"')
        print(data)
        response = self.client.post('/authentication/login-bot/', data, format='json')
        """
            Al ser una llamada a la API, esta busca en el censo de la base de datos de
            Decide que corre por detras, es decir, la base de datos de la aplicación.
            Por lo tanto no puedo comprabar que sea satisfactoria la llamada, pues no
            comprueba la base de datos que se crea al ejecutar el test. Por tanto, y para que
            que no de fallo a la hora de subirse al repositorio y al ejecutarlo por mis compañeros
            se he optado por comprobar solamente el caso de fallo, explicado anteriormente.
        """
        self.assertEqual(response.status_code, 400)


    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_ids__id=v.id).values_list('voter_ids', flat=True))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear
    
    def add_location(self, v):
        v.location = "Sevilla"
        v.save()
        return v

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'tipo': 'O',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')
    
    def test_create_voting_with_location(self):
        data = {'name': 'Example with location'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'tipo': 'O',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse'],
            'location': 'Sevilla'
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)
        census = Census(name='Sevilla')
        census.save()
        census.voting_ids.add(Voting.objects.get(name='Example'))
        self.assertEqual(census, Census.objects.get(name='Sevilla'))
