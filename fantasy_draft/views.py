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
from .utils import to_ordinal, handle_completion

from datetime import datetime, timedelta
import random

def index(request):
    return render(request, 'fantasy_draft/index.html', {})
    
def league_detail(request, invite_sent, league_id):
    league = get_object_or_404(League, pk=league_id)
    
    if league.phase == 'BID':
        league_orders = Order.objects.filter(league=league)
        temp_orders, final_orders = league_orders.filter(is_final=False).exclude(bid=-1), \
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
            'temp_orders': temp_orders,
            'final_orders': final_orders,
            'on_auction': on_auction,
            'auction_ordinal': auction_ordinal,
            'next_user': next_user,
            'high_bid': high_bid,
            'high_bidder': high_bidder,
        })
    elif league.phase == 'SEL':
        # Figure out whose turn it is
        league_orders = Order.objects.filter(league=league)
        next_user = league_orders.get(is_turn=True).user
        
        if request.user.is_authenticated():
            order_num = Order.objects.get(user=request.user, league=league).number
            
            return render(request, 'fantasy_draft/league_detail.html', {
                'league': league,
                'ordinal': to_ordinal(order_num),
                'next_user': next_user,
            })
        else:
            return render(request, 'fantasy_draft/league_detail.html', {
                'league': league,
                'next_user': next_user,
            })
        
    # Standard view
    return render(request, 'fantasy_draft/league_detail.html', {
        'invite_sent': True if invite_sent == 't' else False,
        'league': league,
    })
    
def select_player(request, draft_id, player_id):
    if not request.user.is_authenticated() or request.method != "POST":
        # Weird. This shouldn't ever be happening
        return render(request, 'fantasy_draft/index.html', {})
    else:
        draft = get_object_or_404(Draft, pk=draft_id)
        player = get_object_or_404(Player, pk=player_id)
        
        # Add the player to the given draft
        draft.players.add(player)
        draft.save()
        
        # Switch turns
        league_orders = Order.objects.filter(league=draft.league).order_by('number')
        user_order, league_orders = league_orders.get(user=request.user), list(league_orders)
        user_index = league_orders.index(user_order)
        
        user_order.is_turn = False
        user_order.save()
        
        if draft.league.snake_style and not draft.league.ascending:
            # Descending order
            if user_index == 0:
                if handle_completion(draft):
                    return HttpResponseRedirect('/league/f/' + str(draft.league.id))
                else:
                    next_order = user_order # it's the user's turn again
                    draft.league.ascending = True
                    draft.league.save()
            else:
                next_order = league_orders[user_index - 1]
        else:
            # Ascending order
            if user_index + 1 == len(league_orders):
                if handle_completion(draft):
                    return HttpResponseRedirect('/league/f/' + str(draft.league.id))
                elif draft.league.snake_style:
                    # Snake back around
                    next_order = user_order # it's the user's turn again
                    draft.league.ascending = False
                    draft.league.save()
                else:
                    next_order = league_orders[0]
            else:
                next_order = league_orders[user_index + 1]
            
        next_order.is_turn = True
        next_order.save()
        
        # Quick, back to the league page
        return HttpResponseRedirect('/league/f/' + str(draft.league.id))
    
def bid(request, league_id):
    if not request.user.is_authenticated() or request.method != "POST":
        # This should not be happening
        return render(request, 'fantasy_draft/index.html', {})
    else:
        league = get_object_or_404(League, pk=league_id)
        
        # Update the user's bid
        order = Order.objects.get(user=request.user, league=league)
        order.bid = request.POST['bid']
        order.is_turn = False
        order.save()
        
        # Transition to the next user's turn
        remaining_orders = list(Order.objects.filter(league=league) \
                .filter(is_final=False) \
                .exclude(bid=-1))
                
        user_index = remaining_orders.index(order)
        if user_index + 1 == len(remaining_orders):
            next_order = remaining_orders[0]
        else:
            next_order = remaining_orders[user_index + 1]
            
        next_order.is_turn = True
        next_order.save()
        
        return HttpResponseRedirect(request.GET.get('next', '/'))

def drop_out(request, league_id, on_auction):
    """Drop out of the bidding round."""
    if not request.user.is_authenticated() or request.method != "POST":
        return render(request, 'fantasy_draft/index.html', {})
    else:
        league = get_object_or_404(League, pk=league_id)
        
        # Grab a list of the orders (and, by extension, users) who are still in
        remaining_orders = list(Order.objects.filter(league=league) \
                .filter(is_final=False).exclude(bid=-1))
        
        # Edit the bid value to be the "drop out" signal
        order = Order.objects.get(user=request.user, league=league)
        order.bid = -1
        order.is_turn = False
        order.save()
        
        # Check if there's only one user left in the running
        still_remaining = Order.objects.filter(league=league) \
                .filter(is_final=False).exclude(bid=-1)
        if still_remaining.count() == 1:
            # ...there is!
            order_to_finalize = still_remaining[0]
            
            # Give the user the order that he/she won, and set status to "final"
            order_to_finalize.number = on_auction
            order_to_finalize.is_final = True
            order_to_finalize.save()
            
            # Check on the rest of the bidding progress
            temp_orders = Order.objects.filter(league=league).filter(is_final=False)
            num_orders_left = temp_orders.count()
            if num_orders_left == 1:
                # There's one user left, so he/she gets last pick by default
                last_pick = temp_orders[0]
                last_pick.number = int(on_auction) + 1
                last_pick.is_final = True
                last_pick.save()
            
            if num_orders_left <= 1:
                # The bidding phase is over!
                league.phase = 'SEL'
                league.save()
                
                # Give the turn to the player with order 0
                first_order = Order.objects.filter(league=league).get(number=0)
                first_order.is_turn = True
                first_order.save()
            else:
                # Give the turn to the first player who hasn't got a final order yet
                next_order = temp_orders[0]
                next_order.is_turn = True
                next_order.bid = 0
                next_order.save()
                
                # Reassign all of the rest of the bids to be 0
                for o in temp_orders.exclude(is_turn=True).all():
                    o.bid = 0
                    o.save()
        else:
            # Nope. The round continues
            user_index = remaining_orders.index(order)
            if user_index + 1 == len(remaining_orders):
                next_order = remaining_orders[0]
            else:
                next_order = remaining_orders[user_index + 1]
            
            next_order.is_turn = True
            next_order.save()
        
        return HttpResponseRedirect(request.GET.get('next', '/'))
    
def user_search(request, league_id):
    if request.method == "GET":
        name_input = request.GET['name_input']
        users = []
        
        if name_input is not None and name_input != u"":
            user_set = UserProfile.objects.filter(username__contains=name_input)
            user_set = user_set.extra(select={'length': 'Length(username)'}).order_by('length')
            tournament = get_object_or_404(League, pk=league_id).tournament
            
            # Exclude users that already have a league for this tournament
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
        
def player_search(request, league_id):
    if request.method == "GET":
        tag_input = request.GET['name_input']
        players, league = [], get_object_or_404(League, pk=league_id)
        drafts = league.draft_set
        
        if tag_input is not None and tag_input != u"":
            player_set = league.tournament.player_set.filter(tag__contains=tag_input)
            player_set = player_set.extra(select={'length': 'Length(tag)'}).order_by('length')
            
            # Exclude players that have already been chosen by someone in this league
            # First we'll compile a list of the players that HAVE been chosen...
            chosen_players = []
            for draft in drafts.all():
                chosen_players.extend(list(draft.players.all()))
                
            # And then, if any of those players are in the output, we'll remove them
            for player in player_set:
                if player not in chosen_players:
                    players.append(player)
                    
                    # We'll restrict the size of the output to 5 for now
                    if len(players) > 4:
                        break
        return render(request, 'fantasy_draft/player_search.html', {
            'players': players,
            'draft': drafts.get(user=request.user)
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
    