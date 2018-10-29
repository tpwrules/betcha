from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Week, Game, BettingSheet, Better

class BetterInline(admin.StackedInline):
    model = Better
    can_delete = False
    verbose_name_plural = "better"
    fieldsets = [
        (None,               {'fields':['score','is_active', 'is_winston_cup_participant']}),    ]
  
class GameInline(admin.TabularInline):
    model = Game
    extra = 3

class WeekAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['week_num']}),    ]

class UserAdmin(BaseUserAdmin):
    inlines = (BetterInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Game)
admin.site.register(Week)
"""
class BettingSheetInline(admin.TabularInline):
    model = BettingSheet
    extra = 3

class WeekAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['team_A','team_B','line','TV','team_A_is_favorite','team_A_is_home','team_A_score','team_B_score']}),
        ('Date information', {'fields': ['game_time'], 'classes': ['collapse']}),
    ]
    list_display = ('team_A','team_B','line','TV','team_A_is_Favorite','team_A_is_Home','team_A_score','team_B_score','game_time')
    inlines = [GameInline]
	
admin.site.register(Week, WeekAdmin)"""

