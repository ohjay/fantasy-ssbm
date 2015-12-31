from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.template import RequestContext, loader
from datetime import datetime, timedelta

from .models import *

def index(request):
    return render(request, 'fantasy_draft/index.html', {})
    
def league_detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    return render(request, 'fantasy_draft/league_detail.html', {'league': league})
    
def draft_detail(request, draft_id):
    draft = get_object_or_404(Draft, pk=draft_id)
    return render(request, 'fantasy_draft/draft_detail.html', {'draft': draft})
    
def select_player(request, draft_id):
    draft = get_object_or_404(Draft, pk=draft_id)
    try:
        player = draft.get(pk=request.POST['player_selection'])
    except (KeyError, Player.DoesNotExist):
        return render(request, 'fantasy_draft/league_detail.html', {
            'draft': draft,
            'error_message': "Filler error message in views.py; change later",
        })
    else:
        draft.players += player
        draft.save()
        return HttpResponseRedirect(reverse('fantasy_draft:drafts', args=(d.id,)))

def player_rankings(request):
    context = {'date_now': datetime.now().date, 
               'date_1yr_ago': (datetime.now() - timedelta(days=365)).date}
    return render(request, 'fantasy_draft/player_rankings.html', context)
    
def create_league(request):
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/create.html', context)
    
def leagues(request):
    tournaments, user_leagues = Tournament.objects.all(), request.user.leagues
    tournament_leagues = []
    
    # Fill in tournament_leagues (a list of tournaments and their corresponding leagues)
    for t in tournaments:
        user_tleague = user_leagues.filter(tournament__name=t.name).first()
        if user_tleague is None:
            tournament_leagues.append((t, None))
        else:
            tournament_leagues.append((t, user_tleague))
    
    context = {'tournament_leagues': tournament_leagues}
    return render(request, 'fantasy_draft/leagues.html', context)
    
def standings(request):
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/standings.html', context)
    
def login(request):
    return render(request, 'fantasy_draft/login.html', {})
    
def register(request):
    return render(request, 'fantasy_draft/register.html', {})
    
def info(request):
    return render(request, 'fantasy_draft/info.html', {})
    
def profile(request):
    context = {'user': request.user}
    return render(request, 'fantasy_draft/profile.html', context)
    
def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            template = loader.get_template('fantasy_draft/index.html')
            context = RequestContext(request, {})
            return HttpResponse(template.render(context))
        else:
            return render_to_response('fantasy_draft/login.html', 
                    context_instance=RequestContext(request, {'incorrect_log_in': True}))
    else:
        return render_to_response('fantasy_draft/login.html', 
                context_instance=RequestContext(request, {'incorrect_log_in': True}))
                
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))
    