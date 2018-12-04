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

class BettingSheetAdmin(admin.ModelAdmin):
    model = BettingSheet
    fields = ['paid_for']
    list_display = ['__str__', 'paid_for']
    list_editable = ['paid_for']
    list_display_links = None
    ordering = ['-week', 'better']

    def has_add_permission(self, request, obj=None):
        # the admin can't add betting sheets cause they might not
        # set up the relations correctly
        return False

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Game)
admin.site.register(Week, WeekAdmin)
admin.site.register(BettingSheet, BettingSheetAdmin)
