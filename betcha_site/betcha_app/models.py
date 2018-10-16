from django.db import models

# the Game model
# this stores details about who played in the game,
# where to watch it, and what the result was
class Game(models.Model):
    week = models.ForeignKey("Week", on_delete=models.CASCADE)

    # who is first of Vs.
    team_A = models.CharField(max_length=200)
    # who is second of Vs.
    team_B = models.CharField(max_length=200)

    team_A_is_favorite = models.BooleanField()
    team_A_is_home = models.BooleanField()

    # how to see the game
    tv_channel = models.CharField(max_length=200)
    game_time = models.DateTimeField()

    # betting and score
    line = models.DecimalField(max_digits=5, decimal_places=1)
    team_A_score = models.PositiveIntegerField()
    team_B_score = models.PositiveIntegerField()
    
    def __str__(self):
        return "{} vs. {}".format(self.team_A, self.team_B)

class Week(models.Model):
    week_num = models.PositiveIntegerField()

    # game of the week
    game_of_such = models.ForeignKey(Game, on_delete=models.CASCADE,
        blank=True, null=True, related_name="game_of_week")

class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    # stored properly hashed
    password = models.CharField(max_length=200)

    is_winston_cup_participant = models.BooleanField()
    is_admin = models.BooleanField()

class BettingSheet(models.Model):
    better = models.ForeignKey(User, on_delete=models.CASCADE)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)

    # the admin certifies the user has paid for this sheet
    paid_for = models.BooleanField()

    # not mandatory
    high_risk_bet = models.ForeignKey("Bet",
        blank=True, null=True, on_delete=models.CASCADE)

    # game of the week points bet
    gotw_points = models.PositiveIntegerField()

class Bet(models.Model):
    team_A = models.BooleanField()

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    betting_sheet = models.ForeignKey(BettingSheet, on_delete=models.CASCADE)
