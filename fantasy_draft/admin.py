from django.contrib import admin

from .models import League, Player, Draft # objects with an admin interface
    
class DraftInline(admin.TabularInline):
    model = Draft
    extra = 2
    
class DraftAdmin(admin.ModelAdmin):
    list_display = ('league', 'user')
    search_fields = ['user']
    
class LeagueAdmin(admin.ModelAdmin):
    inlines = [DraftInline]
    
class PlayerAdmin(admin.ModelAdmin):
    fields = ['tag', 'name']
    search_fields = ['tag']

admin.site.register(League, LeagueAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Draft, DraftAdmin)
