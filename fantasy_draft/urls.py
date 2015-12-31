from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /fantasy_draft/
    url(r'^$', views.index, name='index'),
    # ex: /fantasy_draft/2/1
    url(r'^[0-9]+/(?P<draft_id>[0-9]+)/$', views.draft_detail, name='draft_detail'),
    # ex: /fantasy_draft/2/1/select
    url(r'^[0-9]+/(?P<draft_id>[0-9]+)/select/$', views.select_player, name='select'),
    # ex: /fantasy_draft/players
    url(r'^player_rankings/$', views.player_rankings, name='player_rankings'),
    # ex: /fantasy_draft/leagues
    url(r'^leagues/$', views.leagues, name='leagues'),
    # ex: /fantasy_draft/results
    url(r'^standings/$', views.standings, name='standings'),
    # ex: /fantasy_draft/login
    url(r'^login/$', views.login, name='login'),
    # ex: /fantasy_draft/login
    url(r'^register/$', views.register, name='register'),
    # ex: /fantasy_draft/info
    url(r'^info/$', views.info, name='info'),
]
