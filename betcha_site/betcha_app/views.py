from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import models

@login_required
def index(request):
    # to do: figure out how to decide the viewed week
    view_week = 2

    better = request.user.better

    # load the week from the database
    this_week = models.Week.objects.filter(week_num=view_week)[0]
    
    # from the week, we can get all the games happpening
    games = models.Game.objects.filter(week=this_week).order_by('id')
    # the user's betting sheet lets us look up all the related bets
    betting_sheet = models.BettingSheet.objects.filter(
        better=better, week=this_week)
    if len(betting_sheet) == 0: # user doesn't have a betting sheet for this week
        # so let's make one
        betting_sheet = models.BettingSheet(
            better=better,
            week=this_week,
            paid_for=False,
            gotw_points=0)
        betting_sheet.save()
    else:
        betting_sheet = betting_sheet[0]

    # load all of the bets this sheet contains
    sheet_bets = models.Bet.objects.filter(betting_sheet=betting_sheet)
    # now pair all the games with their bets 
    bets_for_game = {}
    # assume no bets have been placed
    for game in games:
        bets_for_game[game] = None
    # check the found bets and mark the games which have them
    for bet in sheet_bets:
        bets_for_game[bet.game] = bet

    # update any bets if the user wants
    if request.method == "POST":
        # save the game IDs for all the games this week so we
        # can figure out which bet needs to be updated
        game_ids = {}
        for game in bets_for_game.keys():
            game_ids[game.id] = game
            
        updates = {}
        # find the post objects that look like bets and record them
        for var, val in request.POST.items():
            try:
                if not var.startswith("g"): continue
                game_id = int(var[1:])
                if val not in ("A", "B"): continue
                # will throw a KeyError if a h4x0r is trying to POST
                # a game not in this week
                updates[game_ids[game_id]] = val
            except:
                pass
        # now apply the user's choices to the bets
        for game, bet_val in updates.items():
            bet = bets_for_game.get(game)
            # bet may not already exist
            if bet is None:
                bet = models.Bet(game=game, better=better,
                    betting_sheet=betting_sheet)
                bets_for_game[game] = bet
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
                the_bet = bets_for_game[game_ids[game_id]]
                betting_sheet.high_risk_bet = the_bet
                updated_betting_sheet = True
        except:
            # probably an error is warranted here too
            pass

        if updated_betting_sheet:
            betting_sheet.save()


    # tag the high risk bet so the template will show it
    for bet in bets_for_game.values():
        if bet is None: continue
        if bet == betting_sheet.high_risk_bet:
            bet.high_risk_check = "checked"
        else:
            bet.high_risk_check = ""

    # now that we know, un-dictionary the results
    # and sort by game ID so every user sees the same thing every time
    bet_data = list(bets_for_game.items())
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