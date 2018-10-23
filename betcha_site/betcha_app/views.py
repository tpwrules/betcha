from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from . import models

@login_required
def index(request):
    # for now, just load any games the database has
    games = models.Game.objects.all()
    return render(request, 'betcha_app/betting_website_sample.html', 
        {"games": games, "user": request.user})