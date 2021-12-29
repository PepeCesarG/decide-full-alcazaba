from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms

from base import mods
from base.models import Auth, Key


class Question(models.Model):
    TYPES = [
        ('O', 'Options'),
        ('B', 'Binary')
    ]

    desc = models.TextField()
    tipo = models.CharField(max_length=1, choices=TYPES, default='O')  
    
    def __str__(self): 
        return self.desc

@receiver(post_save, sender=Question)
def my_handler(sender, instance, **kwargs):
    if instance.tipo == 'B':
        instance.options.all().delete()
        instance.options.create(option='Yes')
        instance.options.create(option='No')


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()
    def save(self, *args, **kwargs):
        if self.question.tipo == 'B' and self.option != 'Yes' and self.option != 'No':
            return
        
        if not self.number:
            self.number = self.question.options.count() + 2
            return super().save(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)

class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)
    
    PROVINCIAS = [
    ('', 'Seleccionar provincia...'),
    ('Alava', 'Álava'),
    ('Albacete', 'Albacete'),
    ('Alicante', 'Alicante'),
    ('Almeria', 'Almería'),
    ('Asturias', 'Asturias'),
    ('Avila', 'Ávila'),
    ('Badajoz', 'Badajoz'),
    ('Barcelona', 'Barcelona'),
    ('Burgos', 'Burgos'),
    ('Caceres', 'Cáceres'),
    ('Cadiz', 'Cádiz'),
    ('Cantabria', 'Cantabria'),
    ('Castellon', 'Castellón'),
    ('Ciudad Real', 'Ciudad Real'),
    ('Cordoba', 'Córdoba'),
    ('Cuenca', 'Cuenca'),
    ('Gerona', 'Gerona'),
    ('Granada', 'Granada'),
    ('Guadalajara', 'Guadalajara'),
    ('Guipuzcoa', 'Guipúzcoa'),
    ('Huelva', 'Huelva'),
    ('Huesca', 'Huesca'),
    ('Islas Baleares', 'Islas Baleares'),
    ('Jaen', 'Jaén'),
    ('La Coruna', 'La Coruña'),
    ('La Rioja', 'La Rioja'),
    ('Las Palmas', 'Las Palmas'),
    ('Leon', 'León'),
    ('Lerida', 'Lérida'),
    ('Lugo', 'Lugo'),
    ('Madrid', 'Madrid'),
    ('Malaga', 'Málaga'),
    ('Murcia', 'Murcia'),
    ('Navarra', 'Navarra'),
    ('Orense', 'Orense'),
    ('Palencia', 'Palencia'),
    ('Pontevedra', 'Pontevedra'),
    ('Salamanca', 'Salamanca'),
    ('Santa Cruz de Tenerife', 'Santa Cruz de Tenerife'),
    ('Segovia', 'Segovia'),
    ('Sevilla', 'Sevilla'),
    ('Soria', 'Soria'),
    ('Tarragona', 'Tarragona'),
    ('Teruel', 'Teruel'),
    ('Toledo', 'Toledo'),
    ('Valencia', 'Valencia'),
    ('Valladolid', 'Valladolid'),
    ('Vizcaya', 'Vizcaya'),
    ('Zamora', 'Zamora'),
    ('Zaragoza', 'Zaragoza'),
]

    location = models.CharField(choices=PROVINCIAS, max_length=50, blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [[i['a'], i['b']] for i in votes]

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''
        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []
        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
