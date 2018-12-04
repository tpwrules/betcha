from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import models

@login_required
def index(request, view_week=None):
    # current week is the latest week that's not hidden
    the_weeks = list(models.Week.objects.filter(hidden=False).all())
    the_weeks.reverse()
    if len(the_weeks) == 0:
        raise Http404("No non-hidden weeks!")
    this_week = the_weeks[0]

    if view_week is None:
        view_week = this_week
    else:
        try:
            view_week = models.Week.objects.get(season_year=2018,
                week_num=view_week)
        except models.Week.DoesNotExist:
            raise Http404("That week doesn't exist.")

    if view_week.hidden:
        raise Http404("That week is hidden.")

    week_pos = the_weeks.index(view_week)
    try:
        last_week = the_weeks[week_pos+1]
    except:
        last_week = None
    if week_pos > 0:
        next_week = the_weeks[week_pos-1]
    else:
        next_week = None

    better = request.user.better

    # errors to show to the user regarding their bet status
    errors = []

    games = view_week.games.all()
    try:
        betting_sheet = better.betting_sheets.get(week=view_week)
    except models.BettingSheet.DoesNotExist:
        # we have to make one the first time the user looks at it
        betting_sheet = models.BettingSheet(
            better=better,
            week=view_week,
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
    if request.method == "POST" and view_week.locked:
        # this shouldn't really happen in normal operation,
        # unless the administrator locks a week somebody is working on
        # but ideally the user will be smart enough to not be editing
        # so close to the deadline
        errors.append("nice try, hacko. "+
            "betulation on lockerized weeks is banned!!!!")
    elif request.method == "POST":
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
            gotw_bet = int(request.POST["points_gotw"])
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

    return render(request, 'betcha_app/main_sheet.html', 
        {"bet_data": bet_data, "user": request.user,
         "view_week": view_week, "betting_sheet": betting_sheet,
         "no_high_risk_check": no_high_risk_check,
         "errors": errors, "this_week": this_week,
         "last_week": last_week, "next_week": next_week})

@login_required
def week(request, week):
    return index(request, view_week=week)

@login_required
def past_weeks(request):
    better = request.user.better
    # look up all the better's sheets and order them to most recent
    sheets = better.betting_sheets.filter(paid_for=True).order_by('-week')

    def gen_weeks():
        for sheet in sheets:
            week = sheet.week
            scores = week.calculate_rank()
            # look for us in the ranking
            our_score = next(s for s in enumerate(scores) if s[1][0] == better)
            position, score = our_score[0], our_score[1][1]
            info = "{}{} out of {} with {} points".format(
                position+1,
                ["st", "nd", "rd"][position] if position < 3 else "th",
                len(scores),
                score
            )
            yield (week, info)

    return render(request, 'betcha_app/past_weeks.html',
        {"user": request.user, "weeks": gen_weeks()})

@login_required
def winston(request):
    better = request.user.better

    if not better.is_winston_cup_participant:
        # template will complain to the user that they shouldn't be here
        return render(request, 'betcha_app/winston.html',
            {"user": request.user})

    # so Season really should be its own Model
    # but it isn't, and i don't want to change the database
    # so, get all the unique weeks and figure out their season
    # so we have a list of all the seasons

    # also i would just use .distinct, but SQLite doesn't support it
    # allegedly. sigh

    # make a set of all the found seasons. this will deduplicate them
    seasons = list({week.season_year for week in models.Week.objects.all()})
    # sort it so the seasons show up in order
    seasons.sort(reverse=True)

    # calculate the winston scores across all users and seasons
    def gen_rankings():
        betters = list(models.Better.objects.filter(
            is_active=True, is_winston_cup_participant=True))
        for season in seasons:
            rankings = list((better, better.calculate_winston_cup_score(season))
                for better in betters)
            # sort by score first, then by user ID so ties end up with a
            # consistent ranking
            rankings.sort(key=lambda r: (-r[1], r[0].id))
            yield rankings
    all_rankings = list(gen_rankings())

    # now calculate the user's past winston cup accolades
    def gen_season_info():
        for season, ranking in zip(seasons, all_rankings):
            # find ourselves better in the rankings
            our_score = next(s for s in enumerate(ranking) if s[1][0] == better)
            position, score = our_score[0], our_score[1][1]
            info = "{}{} out of {} with {} points".format(
                position+1,
                ["st", "nd", "rd"][position] if position < 3 else "th",
                len(ranking),
                score
            )
            yield (season, info)

    return render(request, 'betcha_app/winston.html',
        {"user": request.user, "rankings": all_rankings[0],
        "season_info": gen_season_info()})