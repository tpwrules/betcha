from django.db import models
from django.contrib.auth.models import User

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
    team_A_score = models.PositiveIntegerField(blank=True, null=True)
    team_B_score = models.PositiveIntegerField(blank=True, null=True)
    
    def __str__(self):
        return "{} vs. {}".format(self.team_A, self.team_B)

    @property
    def favorite(self):
        return self.team_A if self.team_A_is_favorite else self.team_B

    @property
    def underdog(self):
        return self.team_B if self.team_A_is_favorite else self.team_A
		
    @property
    def favorite_letter(self):
        return "A" if self.team_A_is_favorite else "B"

    @property
    def underdog_letter(self):
        return "B" if self.team_A_is_favorite else "A"

    @property
    def favorite_is_home(self):
        return self.team_A_is_favorite is self.team_A_is_home

class Week(models.Model):
    week_num = models.PositiveIntegerField()
    season_year = models.PositiveIntegerField()

    # if True, this week is not available to view or bet
    # by default, the interface shows the week with the highest season
    # and week that is not marked hidden
    hidden = models.BooleanField()

    # if True, user bets for this week can no longer be changed
    locked = models.BooleanField()

    # related_name = '+' -> no backwards relationship
    game_of_such = models.OneToOneField(Game, on_delete=models.CASCADE,
        blank=True, null=True, related_name="+")

class Better(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # if True, the user's score is shown and factored into the rankings
    is_active = models.BooleanField()

    is_winston_cup_participant = models.BooleanField()

class BettingSheet(models.Model):
    better = models.ForeignKey(Better, on_delete=models.CASCADE)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)

    # the admin certifies the user has paid for this sheet
    paid_for = models.BooleanField()

    # not mandatory
    # related_name = '+' -> no backwards relationship
    high_risk_bet = models.OneToOneField("Bet",
        blank=True, null=True, on_delete=models.CASCADE, related_name="+")

    # game of the week points bet
    gotw_points = models.PositiveIntegerField()

class Bet(models.Model):
    team_A = models.BooleanField()

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    better = models.ForeignKey(Better, on_delete=models.CASCADE)
    betting_sheet = models.ForeignKey(BettingSheet, on_delete=models.CASCADE)

    def favorite_check(self):
        return "checked" if self.team_A is self.game.team_A_is_favorite else ""

    def underdog_check(self):
        return "checked" if self.team_A is not self.game.team_A_is_favorite else ""
