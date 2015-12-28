from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /fantasy_draft/
    url(r'^$', views.index, name='index'),
    # ex: /fantasy_draft/2
    url(r'^(?P<league_id>[0-9]+)/$', views.league_detail, name='league_detail'),
    # ex: /fantasy_draft/2/1
    url(r'^[0-9]+/(?P<draft_id>[0-9]+)/$', views.draft_detail, name='draft_detail'),
    # ex: /fantasy_draft/2/1/select
    url(r'^[0-9]+/(?P<draft_id>[0-9]+)/select/$', views.select_player, name='select'),
    # ex: /fantasy_draft/players
    url(r'^player_rankings/$', views.player_rankings, name='player_rankings'),
    # ex: /fantasy_draft/create_league
    url(r'^create_league/$', views.create_league, name='create_league'),
    # ex: /fantasy_draft/drafts
    url(r'^drafts/$', views.drafts, name='drafts'),
    # ex: /fantasy_draft/results
    url(r'^standings/$', views.standings, name='standings'),
    # ex: /fantasy_draft/loginreg
    url(r'^loginreg/$', views.loginreg, name='loginreg'),
]
