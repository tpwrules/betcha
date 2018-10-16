from django.db import models
import datetime
from django.utils import timezone

class Game(models.Model):
    team_A = models.CharField(max_length=200)
    team_B = models.CharField(max_length=200)
    line= DecimalField(5,1)
    TV= models.DateTimeField()
    pub_date = models.DateTimeField('date published')
    
    team_A_is_Favorite=models.BooleanField(default=False)
    team_A_is_Home=models.BooleanField(default=False)
    
    team_A_score=models.IntegerField(default=0)
	team_B_score=models.IntegerField(default=0)
    
    def __str__(self):
        self_string=favoriteTeam+" vs "+underDog
        return self.self_string

