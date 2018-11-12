from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group

from .models import Week, Game, BettingSheet, Better


class BetterInline(admin.StackedInline):
    model = Better
    can_delete = False
    verbose_name_plural = "better"
    fieldsets = [
        (None,               {'fields':['is_active', 'is_winston_cup_participant']}),    ]
  
class GameInLine(admin.TabularInline):
    model = Game
    extra = 1

class WeekAdmin(admin.ModelAdmin):
    fields= ['week_num', 'season_year','hidden','locked','game_of_such']
    inlines=[GameInLine]
    

class UserAdmin(BaseUserAdmin):
    inlines = (BetterInline,)

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Game)
admin.site.register(Week, WeekAdmin)
