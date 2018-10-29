from django.db import models
from django.contrib.auth.models import User

# the Game model
# this stores details about who played in the game,
# where to watch it, and what the result was
class Game(models.Model):
    week = models.ForeignKey("Week", on_delete=models.CASCADE,
        related_name="games")

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

    # template helper functions

    def favorite(self):
        return self.team_A if self.team_A_is_favorite else self.team_B

    def underdog(self):
        return self.team_B if self.team_A_is_favorite else self.team_A
		
    def favorite_letter(self):
        return "A" if self.team_A_is_favorite else "B"

    def underdog_letter(self):
        return "B" if self.team_A_is_favorite else "A"

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
    game_of_such = models.OneToOneField(Game, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="+")

    def __str__(self):
        return "Season {} Week {}".format(self.season_year, self.week_num )
		
    def calculate_rank(self, current_week):
        all_betters = models.Better.objects.all()
        rank_list = {}
		# Loops through all betters
        for better in all_betters:
            count = current_week
            score = 0
			# Loops from Week current_week to Week 1
            while count > 0:
                current_betting_sheet = betting_sheet.get(better=better,week=count)
                if not current_betting_sheet.better.is_active or not current_betting_sheet.better.paid_for:
                    break
                else:
                    bets_of_week = current_betting_sheet.bets.all()
					# Loops through all bets on betting sheet and checks if the better was right
                    for game in bets_of_week:
                        if game.team_A_score > game.team_B_score and bet.team_A:
                            score = score + 1
                        elif game.team_B_score > game.team_A_score and not bet.team_A:
                            score = score + 1
                count = count - 1
            rank_list[better.user.username] = score
    return rank_list

class Better(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # if True, the user's score is shown and factored into the rankings
    is_active = models.BooleanField()

    is_winston_cup_participant = models.BooleanField()

class BettingSheet(models.Model):
    better = models.ForeignKey(Better, on_delete=models.CASCADE,
        related_name="betting_sheets")
    week = models.ForeignKey(Week, on_delete=models.CASCADE,
        related_name="betting_sheets")

    # the admin certifies the user has paid for this sheet
    paid_for = models.BooleanField()

    # not mandatory
    # related_name = '+' -> no backwards relationship
    high_risk_bet = models.OneToOneField("Bet",
        blank=True, null=True, on_delete=models.SET_NULL, related_name="+")

    # game of the week points bet
    gotw_points = models.PositiveIntegerField()

class Bet(models.Model):
    team_A = models.BooleanField()

    game = models.ForeignKey(Game, on_delete=models.CASCADE,
        related_name="bets")
    better = models.ForeignKey(Better, on_delete=models.CASCADE,
        related_name="bets")
    betting_sheet = models.ForeignKey(BettingSheet, on_delete=models.CASCADE,
        related_name="bets")

    # template helper functions

    def favorite_check(self):
        return "checked" if self.team_A is self.game.team_A_is_favorite else ""

    def underdog_check(self):
        c = "checked" if self.team_A is not self.game.team_A_is_favorite else ""
        return c

    def high_risk_check(self):
        return "checked" if self == self.betting_sheet.high_risk_bet else ""
