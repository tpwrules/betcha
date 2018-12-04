from django.db import models
from django.contrib.auth.models import User
import django.urls

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

    def favorite_score(self):
        # calculate the score string to display on the template
        score = \
            self.team_A_score if self.team_A_is_favorite else self.team_B_score
        # return nothing if there is no score
        if score is None:
            return ""
        return " ({} point{})".format(score, "" if score == 1 else "s")

    def underdog_score(self):
        # calculate the score string to display on the template
        score = \
            self.team_A_score if not self.team_A_is_favorite else \
            self.team_B_score
        # return nothing if there is no score
        if score is None:
            return ""
        return " ({} point{})".format(score, "" if score == 1 else "s")

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
        return "Season {} Week {}".format(self.season_year, self.week_num)
		
    def calculate_rank(self):
        score_for_better = {}
        for sheet in self.betting_sheets.all():
            # inactive users aren't allowed to bet
            if sheet.better.is_active is False: continue
            score_for_better[sheet.better] = (sheet, sheet.calculate_score())
        # generate list of (better, (sheet, score))
        scores = list(score_for_better.items())
        if self.game_of_such is not None and \
            self.game_of_such.team_A_score is not None and \
            self.game_of_such.team_B_score is not None:
                gotw_score = self.game_of_such.team_A_score + \
                    self.game_of_such.team_B_score
        else:
            gotw_score = 0
        # sort it by score descending, then by game of the week score difference
        # ascending, then by then by the ID of the better (in case of ties)
        scores.sort(key=lambda s: 
            (-s[1][1], abs(s[1][0].gotw_points-gotw_score), s[0].id))
        # remove the betting sheet and return as a list
        # (maybe in the future we can keep it for eg hyperlinks?)
        return list(map(lambda s: (s[0], s[1][1]), scores))

    def get_absolute_url(self):
        return django.urls.reverse("sheet", args=[str(self.week_num)])

class Better(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # if True, the user's score is shown and factored into the rankings
    is_active = models.BooleanField()

    is_winston_cup_participant = models.BooleanField()
	
    def calculate_winston_cup_score(self, season_year):
        winston_cup_score = 0
        for sheet in self.betting_sheets.filter(season_year=season_year, is_active=True):
			winston_cup_score = winston_cup_score + sheet.calculate_score()
        return winston_cup_score				

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

    def calculate_score(self):
        # score is the sum of all the bets on this sheet
        # 1 if True (correct) or 0 if False (incorrect)
        return sum(map(lambda b: b.check_if_correct(), 
            self.bets.all()))

class Bet(models.Model):
    team_A = models.BooleanField()

    game = models.ForeignKey(Game, on_delete=models.CASCADE,
        related_name="bets")
    better = models.ForeignKey(Better, on_delete=models.CASCADE,
        related_name="bets")
    betting_sheet = models.ForeignKey(BettingSheet, on_delete=models.CASCADE,
        related_name="bets")

    def check_if_correct(self):
        score_A, score_B = self.game.team_A_score, self.game.team_B_score
        if score_A is None or score_B is None:
            # potentially the admin hasn't entered the score for this game yet
            # so treat it as an incorrect bet
            return False
        elif score_A == score_B:
            # the players tied
            # idk what the rules are for this, but throw em a bone for now
            return True
        elif score_A > score_B and self.team_A:
            # team A won and the better predicted it
            return True
        elif score_A < score_B and not self.team_A:
            # team B won and the better predicted it
            return True
        else:
            # wrong!!!
            return False

    # template helper functions

    def favorite_check(self):
        return "checked" if self.team_A is self.game.team_A_is_favorite else ""

    def underdog_check(self):
        c = "checked" if self.team_A is not self.game.team_A_is_favorite else ""
        return c

    def high_risk_check(self):
        return "checked" if self == self.betting_sheet.high_risk_bet else ""
