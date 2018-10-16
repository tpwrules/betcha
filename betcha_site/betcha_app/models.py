from django.db import models

# the Game model
# this stores details about who played in the game,
# where to watch it, and what the result was
class Game(models.Model):
    # who is first of Vs.
    team_A = models.CharField(max_length=200)
    # who is second of Vs.
    team_B = models.CharField(max_length=200)

    team_A_is_favorite = models.BooleanField()
    team_B_is_favorite = models.BooleanField()

    # how to see the game
    tv_channel = models.CharField(max_length=200)
    game_time = models.DateTimeField()

    # betting and score
    line = models.DecimalField(5, 1) #
    team_A_score = models.PositiveIntegerField()
    team_B_score = models.PositiveIntegerField()
    
    def __str__(self):
        return "{} vs. {}".fromat(self.team_A, self.team_B)