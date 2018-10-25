from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import models

@login_required
def index(request):
    # to do: figure out how to decide the viewed week
    view_week = 1

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

    # now that we know, un-dictionary the results
    # and sort by game ID so every user sees the same thing every time
    bet_data = list(bets_for_game.items())
    bet_data.sort(key=lambda g: g[0].id)

    return render(request, 'betcha_app/betting_website_sample.html', 
        {"bet_data": bet_data, "user": request.user,"week":this_week,"betting_sheet":betting_sheet})

@login_required
def profile(request):
    return render(request, 'betcha_app/profile_test_sample.html',
        {"user": request.user,
        "fullname": request.user.first_name + " " + request.user.last_name})