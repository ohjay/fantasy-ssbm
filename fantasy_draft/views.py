from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import League, Draft, Player

def index(request):
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/index.html', context)

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

def plsearch(request):
    # edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/pl_search.html', context)

def players(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/players.html', context)
    
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
    
def results(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/results.html', context)
    
def login(request):
    #edit this
    league_list = League.objects.order_by('id')[:5]
    context = {'league_list': league_list}
    return render(request, 'fantasy_draft/login.html', context)
    