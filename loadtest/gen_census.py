import json
import requests


HOST = "http://127.0.0.1:8081"
USER = "davisito"
PASS = "diamante1"
VOTING = [1]


def create_voters(filename):
    """
    Create voters with requests library from filename.json, where key are
    usernames and values are the passwords.
    """
    with open(filename) as f:
        voters = json.loads(f.read())

    data = {'username': USER, 'password': PASS}
    response = requests.post(HOST + '/authentication/login/', data=data)
    token = response.json()

    voters_pk = []
    invalid_voters = []
    for username, pwd in voters.items():
        token.update({'username': username, 'password': pwd})
        response = requests.post(HOST + '/authentication/register/', data=token)
        print('Se crea usuario:' + str(response))
        print('Se crea usuario:' + username)
        addvoter = {'user':username, 'location':'Sevilla','edad':'45','genero':'Hombre'}
        response = requests.post(HOST+'/census/voters/',json =addvoter)

        print('Se crea voter:' +str(response.text))
        if response.status_code == 201:
            
            voters_pk.append(int(response.text))
        else:
            invalid_voters.append(username)
    return voters_pk, invalid_voters


def add_census(voters_pk, voting_pk):
    """
    Add to census all voters_pk in the voting_pk.
    """
    data = {'username': USER, 'password': PASS}
    response = requests.post(HOST + '/authentication/login/', data=data)
    token = response.json()

    data2 = {'name': 'censo Locust','voters': voters_pk, 'votings': voting_pk}
    auth = {'Authorization': 'Token ' + token.get('token')}
    response = requests.post(HOST + '/census/', json=data2, headers=auth)
    print("La respuesta es: " + response.text)



voters, invalids = create_voters('voters.json')
print(voters,invalids)

add_census(voters, VOTING)
print("Create voters with pk={0} \nInvalid usernames={1}".format(voters, invalids))