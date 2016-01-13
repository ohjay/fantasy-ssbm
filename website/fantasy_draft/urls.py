from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /fantasy_draft/
    url(r'^$', views.index, name='index'),
    # ex: /fantasy_draft/league/t/2
    url(r'^league/(?P<invite_sent>[tf])/(?P<league_id>[0-9]+)/$', views.league_detail, name='league_detail'),
    # ex: /fantasy_draft/user_search/1
    url(r'^user_search/(?P<league_id>[0-9]+)/$', views.user_search, name='user_search'),
    # ex: /fantasy_draft/select_player/483
    url(r'^select_player/(?P<draft_id>[0-9]+)/(?P<player_id>[0-9]+)/$', views.select_player, name='select_player'),
    # ex: /fantasy_draft/players
    url(r'^player_rankings/$', views.player_rankings, name='player_rankings'),
    # ex: /fantasy_draft/leagues
    url(r'^leagues/$', views.leagues, name='leagues'),
    # ex: /fantasy_draft/login
    url(r'^login/$', views.login, name='login'),
    # ex: /fantasy_draft/register
    url(r'^register/$', views.register, name='register'),
    # ex: /fantasy_draft/info
    url(r'^info/$', views.info, name='info'),
    # ex: /fantasy_draft/profile
    url(r'^profile/$', views.profile, name='profile'),
    # ex: /fantasy_draft/user_logout
    url(r'^user_logout/$', views.user_logout, name='user_logout'),
    # ex: /fantasy_draft/create_league/40
    url(r'^create_league/(?P<t_id>[0-9]+)/$', views.create_league, name='create_league'),
    # ex: /fantasy_draft/invite/3/19
    url(r'^invite/(?P<recipient_id>[0-9]+)/(?P<league_id>[0-9]+)$', views.invite, name='invite'),
    # ex: /fantasy_draft/accept/560
    url(r'^accept/(?P<i_id>[0-9]+)$', views.accept, name='accept'),
    # ex: /fantasy_draft/decline/560
    url(r'^decline/(?P<i_id>[0-9]+)$', views.decline, name='decline'),
    # ex: /fantasy_draft/activate/23
    url(r'^activate/(?P<league_id>[0-9]+)$', views.activate, name='activate'),
    # ex: /fantasy_draft/drop_out/10/2
    url(r'^drop_out/(?P<league_id>[0-9]+)/(?P<on_auction>[0-9]+)$', views.drop_out, name='drop_out'),
    # ex: /fantasy_draft/bid/10
    url(r'^bid/(?P<league_id>[0-9]+)$', views.bid, name='bid'),
    # ex: /fantasy_draft/player_search/10
    url(r'^player_search/(?P<league_id>[0-9]+)/$', views.player_search, name='player_search'),
    # ex: /fantasy_draft/leave/31
    url(r'^leave/(?P<league_id>[0-9]+)$', views.leave, name='leave'),
    # ex: /fantasy_draft/confirm/2304238jskaf0h3
    url(r'^confirm/(?P<activation_key>\w+)/', views.confirm_registration, name='confirm_registration'),
]
