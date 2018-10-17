from django.http import HttpResponse
from django.shortcuts import render

from . import models


def index(request):
    # for now, just load any games the database has
    games = models.Game.objects.all()
    return render(request, 'betcha_app/betting_website_sample.html', 
        {"games": games})