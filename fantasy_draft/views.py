from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.template import RequestContext, loader
from datetime import datetime, timedelta

from .models import League, Draft, Player

def index(request):
    return render(request, 'fantasy_draft/index.html', {})

def league_detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    return render(request, 'fantasy_draft/league_detail.html', {'league': league})
    
def draft_detail(request, draft_id):
    draft = get_object_or_404(Draft, pk=draft_id)
    return render(request, 'fantasy_draft/draft_detail.html', {'draft': draft})
    
def select_player(request, draft_id):
    d = get_object_or_404(Draft, pk=draft_id)
    try:
        selection = d.get(pk=request.POST['player_selection'])
    except (KeyError, Player.DoesNotExist):
        return render(request, 'fantasy_draft/league_detail.html', {
            'draft': d,
            'error_message': "Filler error message in views.py; change later",
        })
    else:
        draft.players += player
        draft.save()
        return HttpResponseRedirect(reverse('fantasy_draft/draft', args=(d.id,)))

def player_rankings(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list, 
               'date_now': datetime.now().date, 
               'date_1yr_ago': (datetime.now() - timedelta(days=365)).date}
    return render(request, 'fantasy_draft/player_rankings.html', context)
    
def create_league(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/create.html', context)
    
def drafts(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/drafts.html', context)
    
def standings(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/standings.html', context)
    
def loginreg(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/login.html', context)
    
def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            template = loader.get_template('fantasy_draft/index.html')
            context = RequestContext(request, {})
            return HttpResponse(template.render(context))
        else:
            return render_to_response('fantasy_draft/login.html', 
                    context_instance=RequestContext(request,{'incorrect_log_in': True}))
    else:
        return render_to_response('fantasy_draft/login.html', 
                context_instance=RequestContext(request,{'incorrect_log_in': True}))
    