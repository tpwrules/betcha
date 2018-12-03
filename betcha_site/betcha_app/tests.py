from django.test import TestCase
from django.urls import reverse
import datetime
from django.utils import timezone

from .models import Game

def create_Game(teamA,teamB,teamAFav,teamAHome):
    return Game.objects.create(team_A=teamA, team_B=teamB,team_A_is_favorite=teamAFav,team_A_is_home=teamAHome)
    
    
class GameModelTests(TestCase):
    def favorite_Test(self):
        example=create_Game(teamA="dog",teamB="notDog",teamAFav=True,teamAHome=True)
        self.assertIs(example.favorite(),"dog")
 
        