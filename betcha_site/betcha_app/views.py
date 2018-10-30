from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import models

@login_required
def index(request):
    # to do: figure out how to decide the viewed week
    view_week = 2

    better = request.user.better

    # errors to show to the user regarding their bet status
    errors = []

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
            if not var.startswith("g"): continue
            try:
                game_id = int(var[1:])
            except ValueError:
                # we got posted a value that's not an integer
                # and so can't be a game ID
                errors.append("Corrupt POST: bet on invalid gid. "+
                    "Please refresh the page and try to bet again.")
                continue
            if val not in ("A", "B"):
                # we got posted a bet that's on neither team A nor B
                errors.append("Corrupt POST: bet invalid val. "+
                    "Please refresh the page and try to bet again.")
                continue
            try:
                updates[game_for_gid[game_id]] = val
            except KeyError:
                # we got posted a bet that's not a game ID for a game
                # on this sheet. catch it so a hacker can't change bets on
                # e.g. locked weeks
                errors.append("Corrupt POST: bet gid not for sheet. "+
                    "Please refresh the page and try to bet again.")
                continue
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
            gotw_bet = int(request.POST["gotw"])
        except KeyError:
            # shouldn't happen because it's in the template
            errors.append("Corrupt POST: missing gotw. "+
                "Please refresh the page and try to bet again.")
        except ValueError:
            # stop the user typing garbage into the game of the week bet
            errors.append(
                "Game of the Week bet must be non-negative integer")
        else:
            # afaik, football game scores can't go below 0
            # so that's not a plausible bet for the user to place
            if gotw_bet < 0:
                errors.append(
                    "Game of the Week bet must be non-negative integer")
            else:
                if betting_sheet.gotw_points != gotw_bet:
                    betting_sheet.gotw_points = gotw_bet
                    updated_betting_sheet = True

        # save the high risk bet
        try:
            high_risk_bet = request.POST["high_risk"]
        except KeyError:
            # shouldn't happen because it's in the template
            errors.append("Corrupt POST: missing high_risk. "+
                "Please refresh the page and try to bet again.")
        else:
            if high_risk_bet == "none":
                if betting_sheet.high_risk_bet is not None:
                    betting_sheet.high_risk_bet = None
                    updated_betting_sheet = True
            elif high_risk_bet.startswith("g"):
                try:
                    game_id = int(high_risk_bet[1:])
                    the_bet = bet_for_game[game_for_gid[game_id]]
                except KeyError:
                    # we got posted an integer that's not an ID for a game
                    # on this sheet. catch it so a hacker doesn't set
                    # their high risk bet for a game they already know
                    # the result to
                    errors.append("Corrupt POST: hrb gid not for sheet. "+
                        "Please refresh the page and try to bet again.")
                except ValueError:
                    # we got posted a value that's not an integer and so
                    # can't be a game ID
                    errors.append("Corrupt POST: hrb invalid gid. "+
                        "Please refresh the page and try to bet again.")
                else:
                    if the_bet is None:
                        # we can't create a bet and set it as high risk
                        # because that would also place a bet for that game
                        # so just tell the user they're bad
                        errors.append("You can't place a high risk bet "+
                            "on a game without also betting on it!")
                    elif betting_sheet.high_risk_bet != the_bet:
                        betting_sheet.high_risk_bet = the_bet
                        updated_betting_sheet = True

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
         "no_high_risk_check": no_high_risk_check,
         "errors": errors})

@login_required
def profile(request):
    return render(request, 'betcha_app/profile_test_sample.html',
        {"user": request.user,
        "fullname": request.user.first_name + " " + request.user.last_name})