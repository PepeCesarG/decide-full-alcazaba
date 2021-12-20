from django.db import models
from voting.models import Voting
from django.contrib.auth.models import User

class Census(models.Model):
    name = models.TextField(unique = True, default = "undefined census")
    voting_ids = models.ManyToManyField(Voting)
    voter_ids = models.ManyToManyField(User)
    
    def votings(self):
        return "\n".join([p.name for p in self.voting_ids.all()])
    
    def voters(self):
        return "\n".join([p.username for p in self.voter_ids.all()])
    
    def __str__(self):
        return self.name

    #class Meta:
        #unique_together = (('voting_ids', 'voter_ids'),)