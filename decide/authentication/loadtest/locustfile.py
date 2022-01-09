import json

from random import choice

from locust import (
    HttpUser,
    SequentialTaskSet,
    TaskSet,
    task,
    between
)

HOST = "http://localhost:8000"


class DefLoginAndLogout(SequentialTaskSet):

    @task
    def login(self):

        with open('users.json') as f:
            user = choice(list(json.loads(f.read()).items()))

        response = self.client.get('/authentication/decide/login/')
        csrftoken = response.cookies['csrftoken']

        username, tuple_data = user

        self.client.post('/authentication/decide/login/',
                         {
                             'username': username,
                             'password': tuple_data[0],
                         },
                         headers={
                             'Content-Type': 'application/x-www-form-urlencoded',
                             'X-CSRFToken': csrftoken
                         })

    @task
    def logout(self):
        self.client.get('/authentication/decide/logout/')


class DefRegister(SequentialTaskSet):

    count = 0
    dni_num = 11111111
    dni_letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    @task
    def register(self):

        response = self.client.get('/authentication/decide/register/')
        csrftoken = response.cookies['csrftoken']

        username = "username" + str(self.count)
        email = "username" + str(self.count) + "@gmail.com"
        dni = str(self.dni_num) + self.dni_letters[self.count % 26]

        data = {
            "firs_name": "Nombre",
            "second_name": "Apellidos",
            "username": username,
            "email": email,
            "password1": "password1234",
            "password2": "password1234",
            "dni": dni,
            "sexo": "Man",
            "titulo": "Software",
            "curso": "First",
            "candidatura": "",
            "edad": "21"
        }

        if self.count % 26 == 25:
            self.dni_num += 1

        self.count += 1

        self.client.post('/authentication/decide/register/',
                         data=data,
                         headers={
                             'Content-Type': 'application/x-www-form-urlencoded',
                             'X-CSRFToken': csrftoken
                         })

    @task
    def logout(self):
        self.client.get('/authentication/decide/logout/')


# For login you need gen_user.py
class Login(HttpUser):
    host = HOST
    tasks = [DefLoginAndLogout]
    wait_time = between(3, 5)


class Register(HttpUser):
    host = HOST
    tasks = [DefRegister]
    wait_time = between(3, 5)
