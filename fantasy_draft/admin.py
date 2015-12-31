from django.contrib import admin

# Objects with an admin interface:
from .models import League, Player, Draft, Result, Tournament, UserProfile
    
class DraftInline(admin.TabularInline):
    model = Draft
    extra = 2
    
class DraftAdmin(admin.ModelAdmin):
    search_fields = ['user']
    
class LeagueAdmin(admin.ModelAdmin):
    inlines = [DraftInline]
    
class PlayerAdmin(admin.ModelAdmin):
    fields = ['tag', 'name', 'tournaments']
    search_fields = ['tag']

admin.site.register(League, LeagueAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Draft, DraftAdmin)
admin.site.register(Tournament)
admin.site.register(Result)
admin.site.register(UserProfile)
