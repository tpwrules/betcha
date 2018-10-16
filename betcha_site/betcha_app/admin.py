from django.contrib import admin

from .models import Week, Game, BettingSheet, User

class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name','email','password','is_winston_cup_participant','is_admin']}),    ]

class BettingSheetInline(admin.TabularInline):
    model = BettingSheet
    extra = 3
    
class GameInline(admin.TabularInline):
    model = Game
    extra = 3


class WeekAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['team_A','team_B','line','TV','team_A_is_favorite','team_A_is_home','team_A_score','team_B_score']}),
        ('Date information', {'fields': ['game_time'], 'classes': ['collapse']}),
    ]
    list_display = ('team_A','team_B','line','TV','team_A_is_Favorite','team_A_is_Home','team_A_score','team_B_score','game_time')
    inlines = [GameInline]
	

admin.site.register(Week, WeekAdmin)
admin.site.register(User, UserAdmin)
