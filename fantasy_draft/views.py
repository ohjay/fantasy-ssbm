from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.template import RequestContext, loader
from datetime import datetime, timedelta

from .models import *
from .forms import *

def index(request):
    return render(request, 'fantasy_draft/index.html', {})
    
def league_detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    return render(request, 'fantasy_draft/league_detail.html', {'league': league})
    
def user_search(request):
    if request.method == "GET":
        name_input = request.GET['name_input']
        if name_input is not None and name_input != u"":
            users = UserProfile.objects.filter(username__contains = name_input)
            users = users.extra(select={'length': 'Length(username)'}).order_by('length')
        else:
            users = []
        # Limit the output to a maximum of 5 results
        return render(request, 'fantasy_draft/user_search.html', {'users': users[:5]})
    
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
    
def create_league(request, t_id):
    if request.user.is_authenticated() and not request.user.leagues.filter(tournament__id=t_id):
        if request.method == 'POST':
            league_form = LeagueForm(data=request.POST)
            if league_form.is_valid(): # it should pretty much always be valid
                # Create a new league and save it
                league = league_form.save(commit=False)
                league.creator = request.user
                league.tournament = Tournament.objects.get(pk=t_id)
                league.save()
                
                # Then add it to the user's collection of leagues
                request.user.leagues.add(league)
                request.user.save()
                
                # Redirect
                return HttpResponseRedirect(reverse('fantasy_draft:leagues'))
        else:
            # Render a blank creation form
            league_form = LeagueForm()
            return render(request, 'fantasy_draft/create_league.html', {
                'league_form': league_form,
                't_id': t_id,
                't_name': Tournament.objects.get(pk=t_id),
            })
    else:
        # Permission denied
        return HttpResponseRedirect(reverse('fantasy_draft:leagues'))
    
def leagues(request):
    if request.user.is_authenticated():
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
    else:
        return render(request, 'fantasy_draft/leagues.html', {})
    
def standings(request):
    return render(request, 'fantasy_draft/standings.html', {})
    
def login(request):
    return render(request, 'fantasy_draft/login.html', {})
    
def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            # Save the new user to the database
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            # Log the user in
            user = authenticate(username=request.POST['username'],
                    password=request.POST['password'])
            auth.login(request, user)
            return HttpResponseRedirect(reverse('fantasy_draft:index'))
        else:
            # Cut the asterisk label out of the error message
            error_msg = user_form.errors.as_text()
            error_msg = error_msg[error_msg.find('*', 1) + 2:]
            
            return render(request, 'fantasy_draft/register.html', {
                'user_form': user_form, 
                'error_msg': error_msg
            })
    else:
        user_form = UserForm()
        return render(request, 'fantasy_draft/register.html', {
            'user_form': user_form, 
            'error_msg': False
        })
    
def info(request):
    return render(request, 'fantasy_draft/info.html', {})
    
def profile(request):
    if request.user.is_authenticated():
        context = {'user': request.user}
        return render(request, 'fantasy_draft/profile.html', context)
    else:
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
    
def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('fantasy_draft:index'))
        else:
            return render_to_response('fantasy_draft/login.html', 
                    context_instance=RequestContext(request, {'incorrect_log_in': True}))
    else:
        return render_to_response('fantasy_draft/login.html', 
                context_instance=RequestContext(request, {'incorrect_log_in': True}))
                
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))
    