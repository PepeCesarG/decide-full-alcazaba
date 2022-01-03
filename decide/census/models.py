from django.db import models
from voting.models import Voting
from django.contrib.auth.models import User
import logging 
class Voter(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.TextField(max_length = 50, blank = True, null = True)
    edad = models.PositiveIntegerField(blank = True, null = True)
    genero = models.TextField(max_length = 50, blank = True, null = True)
    def __str__(self):
        return self.user.username
 
class Census(models.Model):
    name = models.TextField(unique = True, default = "undefined census")
    
    voting_ids = models.ManyToManyField(Voting, blank=True)
    voter_ids = models.ManyToManyField(Voter)

    
    def votings(self):
        return "\n".join([p.name for p in self.voting_ids.all()])


    def voters(self):
        return "\n".join([str(p) for p in self.voter_ids.all()])
        
    
    def __str__(self):
        return self.name
    
    
    #class Meta:
        #unique_together = (('voting_ids', 'voter_ids'),)

    