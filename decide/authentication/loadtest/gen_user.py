import json
import requests

HOST = "http://localhost:8000"


def create_users(filename):
    with open(filename) as f:

        users = json.loads(f.read())

        for username, tuple_data in users.items():

            data = {
                "username": username,
                "email": username + "@gmail.com",
                "password1": tuple_data[0],
                "password2": tuple_data[0],
                "dni": tuple_data[1],
                "sexo": "Man",
                "titulo": "Software",
                "curso": "First",
                "candidatura": "",
                "edad": "21"
            }

            csrftoken = requests.get(HOST + '/authentication/decide/register/').cookies['csrftoken']

            response = requests.post(HOST + '/authentication/decide/register/', data=data, headers={
                "Content-Type": "application/x-www-form-urlencoded",
                'X-CSRFToken': csrftoken
            })

        print(response.content)


create_users("users.json")