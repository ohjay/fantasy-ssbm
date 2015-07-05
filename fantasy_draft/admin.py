from django.contrib import admin

# Objects with an admin interface:
from .models import League, Player, Draft, TournamentResult, \
        Tournament, Pool, User
    
class DraftInline(admin.TabularInline):
    model = Draft
    extra = 2
    
class DraftAdmin(admin.ModelAdmin):
    list_display = ('league', 'user')
    search_fields = ['user']
    
class LeagueAdmin(admin.ModelAdmin):
    inlines = [DraftInline]
    
class PlayerAdmin(admin.ModelAdmin):
    fields = ['tag', 'name', 'pool', 'placing', 'seed', 'picture', 'description', 'tournaments']
    search_fields = ['tag']

admin.site.register(League, LeagueAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(Tournament)
admin.site.register(TournamentResult)
admin.site.register(Pool)
admin.site.register(User)
