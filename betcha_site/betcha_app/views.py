from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import models

@login_required
def index(request):
    # to do: figure out how to decide the viewed week
    view_week = 2

    better = request.user.better

    # to do: figure out how to decide the viewed season also
    this_week = models.Week.objects.get(
        season_year=2018, week_num=view_week)
    
    games = this_week.games.all()
    try:
        betting_sheet = better.betting_sheets.get(week=this_week)
    except models.BettingSheet.DoesNotExist:
        # we have to make one the first time the user looks at it
        betting_sheet = models.BettingSheet(
            better=better,
            week=this_week,
            paid_for=False,
            gotw_points=0)
        betting_sheet.save()

    # make a dictionary of games to bets so we can render them together
    # start out by saying no game has a bet
    bet_for_game = {game: None for game in games}
    # now check the bets on the betting sheet, and pair each with its game
    for bet in betting_sheet.bets.all():
        bet_for_game[bet.game] = bet

    # process a bet update request from the user
    if request.method == "POST":
        # build a dictionary of game IDs on the sheet to their game objects
        # so we can easily look up bets placed without hitting the database
        # and we get bad post checking for free, too
        game_for_gid = {}
        for game in bet_for_game.keys():
            game_for_gid[game.id] = game
        
        updates = {}
        # find the post objects that look like bets and record them
        for var, val in request.POST.items():
            try:
                if not var.startswith("g"): continue
                # will throw a ValueError if a h4x0r is trying to POST
                # to something that's not a game ID
                game_id = int(var[1:])
                if val not in ("A", "B"): continue
                # will throw a KeyError if a h4x0r is trying to POST
                # a game not in this week
                updates[game_for_gid[game_id]] = val
            except:
                pass
        # now apply the user's choices to the bets
        for game, bet_val in updates.items():
            bet = bet_for_game.get(game)
            # if this is the first bet, the object won't already exist
            if bet is None:
                bet = models.Bet(game=game, better=better,
                    betting_sheet=betting_sheet)
                bet_for_game[game] = bet
            # already validated to be B for team B
            bet.team_A = True if bet_val == "A" else False
            bet.save()

        updated_betting_sheet = False

        # update game of the week field
        try:
            gotw_bet = request.POST["gotw"]
            gotw_bet = int(gotw_bet) 
            if gotw_bet >= 0:
                betting_sheet.gotw_points = gotw_bet
                updated_betting_sheet = True
        except:
            # we should display an error if the request was invalid
            # but for now, the user can just see nothing changed
            # and figure it out themselves
            pass

        # save the high risk bet
        try:
            high_risk_bet = request.POST["high_risk"]
            if high_risk_bet == "none":
                betting_sheet.high_risk_bet = None
                updated_betting_sheet = True
            elif high_risk_bet.startswith("g"):
                # once again, exceptions will be thrown if the POST
                # is up to something
                game_id = int(high_risk_bet[1:])
                the_bet = bet_for_game[game_for_gid[game_id]]
                betting_sheet.high_risk_bet = the_bet
                updated_betting_sheet = True
        except:
            # probably an error is warranted here too
            pass

        if updated_betting_sheet:
            betting_sheet.save()

    bet_data = list(bet_for_game.items())
    # sort by game ID so every user sees the same thing every time
    bet_data.sort(key=lambda g: g[0].id)

    no_high_risk_check = \
        "checked" if betting_sheet.high_risk_bet is None else ""

    return render(request, 'betcha_app/betting_website_sample.html', 
        {"bet_data": bet_data, "user": request.user,
         "week": this_week, "betting_sheet": betting_sheet,
         "no_high_risk_check": no_high_risk_check})

@login_required
def profile(request):
    return render(request, 'betcha_app/profile_test_sample.html',
        {"user": request.user,
        "fullname": request.user.first_name + " " + request.user.last_name})