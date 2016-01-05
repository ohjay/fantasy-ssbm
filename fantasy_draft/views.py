from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.template import RequestContext, loader
from django.db.models import Max

from .models import *
from .forms import *
from .utils import to_ordinal

from datetime import datetime, timedelta
import random

def index(request):
    return render(request, 'fantasy_draft/index.html', {})
    
def league_detail(request, invite_sent, league_id):
    league = get_object_or_404(League, pk=league_id)
    
    if league.phase == 'BID':
        league_orders = Order.objects.filter(league=league)
        temp_orders, final_orders = league_orders.filter(is_final=False), \
                league_orders.filter(is_final=True)
        on_auction = final_orders.count()
        auction_ordinal = to_ordinal(on_auction)
        
        # Determine whose turn it is to bid for order
        next_user = temp_orders.get(is_turn=True).user
        
        # Obtain the value of the current highest bid (+ the winning bidder)
        high_bid = temp_orders.all().aggregate(Max('bid'))['bid__max']
        high_bidder = temp_orders.filter(bid=high_bid)[0].user
        
        return render(request, 'fantasy_draft/league_detail.html', {
            'league': league,
            'final_orders': final_orders,
            'on_auction': on_auction,
            'auction_ordinal': auction_ordinal,
            'next_user': next_user,
            'high_bid': high_bid,
            'high_bidder': high_bidder,
        })
        
    # Standard view
    return render(request, 'fantasy_draft/league_detail.html', {
        'invite_sent': True if invite_sent == 't' else False,
        'league': league,
    })
    
def user_search(request, league_id):
    if request.method == "GET":
        name_input = request.GET['name_input']
        users = []
        
        if name_input is not None and name_input != u"":
            user_set = UserProfile.objects.filter(username__contains = name_input)
            user_set = user_set.extra(select={'length': 'Length(username)'}).order_by('length')
            tournament = get_object_or_404(League, pk=league_id).tournament
            
            for u in user_set:
                exclude = False
                for l in u.leagues.all():
                    # This is acceptable, since each user has a very limited number of leagues
                    if l.tournament == tournament:
                        exclude = True
                        
                if not exclude:
                    users.append(u)
                    if len(users) > 4:
                        # Limit the output to a maximum of 5 users
                        break
        return render(request, 'fantasy_draft/user_search.html', {
            'users': users,
            'league_id': league_id,
        })

def invite(request, recipient_id, league_id):
    if not request.user.is_authenticated() or request.method != "POST":
        # Someone's trying to game the system...
        return render(request, 'fantasy_draft/index.html', {})
    else:
        # Create and send a new invitation
        invitation = Invitation()
        invitation.league = get_object_or_404(League, pk=league_id)
        invitation.sender = request.user
        invitation.recipient = get_object_or_404(UserProfile, pk=recipient_id)
        invitation.save()
        
        # Quick, back to the league page
        return HttpResponseRedirect('/league/t/' + league_id)
        
def accept(request, i_id):
    if not request.user.is_authenticated() or request.method != "POST":
        return render(request, 'fantasy_draft/index.html', {})
    else:
        invitation = get_object_or_404(Invitation, pk=i_id)
        invitation.status = "ACC"
        invitation.save()
        
        Order.objects.create(number=invitation.league.userprofile_set.count(), 
                user=request.user, league=invitation.league)
        
        return HttpResponseRedirect('/league/f/' + str(invitation.league.id))
    
def decline(request, i_id):
    if not request.user.is_authenticated() or request.method != "POST":
        return render(request, 'fantasy_draft/index.html', {})
    else:
        invitation = get_object_or_404(Invitation, pk=i_id)
        invitation.delete()
        
        return HttpResponseRedirect(request.GET.get('next', '/'))
        
def activate(request, league_id):
    """Lock users in and create empty drafts for them."""
    league = get_object_or_404(League, pk=league_id)
    if not request.user.is_authenticated() or request.user != league.creator:
        # Call hax
        return render(request, 'fantasy_draft/index.html', {})
    else:
        # Activate the league
        if league.random_order:
            league.phase = 'SEL'
            
            # Assign a random order for the players
            order_options = list(range(league.userprofile_set.count()))
            for u in league.userprofile_set.all():
                user_order = Order.objects.get(user=u, league=league)
                
                selected_num = random.choice(order_options)
                user_order.number = selected_num
                user_order.save()
                
                order_options.remove(selected_num) # this spot in the ordering is TAKEN, son
        else:
            league.phase = 'BID'
        league.save()
        
        # Create drafts for the users in the league
        for u in league.userprofile_set.all():
            u_draft = Draft()
            u_draft.league = league
            u_draft.user = u
            u_draft.save()
        
        return HttpResponseRedirect(request.GET.get('next', '/'))
    
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
            if league_form.is_valid():
                # Create a new league and save it
                league = league_form.save(commit=False)
                league.creator = request.user
                league.tournament = Tournament.objects.get(pk=t_id)
                league.date_created = datetime.now()
                league.save()
                
                # Then add it to the user's collection of leagues
                Order.objects.create(number=0, user=request.user, league=league, is_turn=True)
                
                # Redirect
                return HttpResponseRedirect(reverse('fantasy_draft:leagues'))
            else:
                error_msg = league_form.errors.as_text()
                
                return render(request, 'fantasy_draft/create_league.html', {
                    'league_form': league_form,
                    't_id': t_id,
                    't_name': Tournament.objects.get(pk=t_id),
                    'error_msg': "[ERROR] " + error_msg,
                })
        else:
            # Render a blank creation form
            league_form = LeagueForm()
            return render(request, 'fantasy_draft/create_league.html', {
                'league_form': league_form,
                't_id': t_id,
                't_name': Tournament.objects.get(pk=t_id),
                'error_msg': False,
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
    