from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.template import RequestContext, loader
from django.db.models import Max
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import *
from .forms import *
from .utils import to_ordinal, handle_completion, get_score, TOURNAMENT_SCHEDULE

from datetime import datetime, date, timedelta
from collections import defaultdict
import random, hashlib, operator

def index(request):
    next_tournament = "No tournaments found."
    next_date = date.today() + timedelta(21) # 20XX wasn't an option
    
    for tournament, day in reversed(TOURNAMENT_SCHEDULE):
        if day <= date.today():
            break
        else:
            next_tournament, next_date = tournament, day
    
    message = request.GET.get('m')
    if not message:
        return render(request, 'fantasy_draft/index.html', {
            'next_tournament': next_tournament,
            'next_date': next_date,
        })
    elif message == '1':
        return render(request, 'fantasy_draft/index.html', {
            'message': "Your account has been successfully activated!",
            'next_tournament': next_tournament,
            'next_date': next_date,
        })
    elif message == '2':
        return render(request, 'fantasy_draft/index.html', {
            'message': "An activation link has been sent to your email.",
            'next_tournament': next_tournament,
            'next_date': next_date,
        })

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
        
        draft_data = None
        if not league.random_order:
            draft_data = [] # [(draft, bid, number)]
            for draft in league.draft_set.all():
                d_order = Order.objects.get(user=draft.user, league=league)
                draft_data.append((draft, d_order.bid, d_order.number))
            
            # Sort by increasing bid amount
            draft_data = sorted(draft_data, key=operator.itemgetter(2))
            
            temp = []
            for draft, bid, number in draft_data:
                temp.append((draft, bid))
            draft_data = temp # [(draft, bid)]
        
        if request.user.is_authenticated() and request.user.is_active:
            order = Order.objects.filter(user=request.user).filter(league=league) # the user's order
            if order:
                order_num = order[0].number
            
                return render(request, 'fantasy_draft/league_detail.html', {
                    'league': league,
                    'ordinal': to_ordinal(order_num),
                    'next_user': next_user,
                    'draft_data': draft_data,
                })
                
        return render(request, 'fantasy_draft/league_detail.html', {
            'league': league,
            'next_user': next_user,
            'draft_data': draft_data,
        })
    elif league.phase == 'COM':
        # Check on scoring (do results exist yet?)
        tournament_results = Result.objects.filter(tournament=league.tournament)
        if tournament_results:
            # Display scores alongside drafts
            draft_scores = [] # a list of drafts and their associated scores
            
            for draft in league.draft_set.all():
                player_placings = [] # a list of players and their associated placings
                
                # Compute the score for each player in the draft
                score = 0
                for player in draft.players.all():
                    player_result = tournament_results.filter(player=player)
                    if player_result:
                        placing = player_result.placing
                        score += get_score(placing)
                    else:
                        placing = '?'
                    player_placings.append((player, placing))
                    
                bid = None
                if not league.random_order:
                    bid = Order.objects.get(user=draft.user, league=league).bid
                    score -= bid
                
                draft_scores.append((draft, player_placings, score, bid))
    
            context = {
                'league': league,
                'draft_scores': draft_scores
            }
            return render(request, 'fantasy_draft/league_detail.html', context)
        elif not league.random_order:
            draft_data = [] # [(draft, bid)]
            for draft in league.draft_set.all():
                draft_data.append((draft, Order.objects.get(user=draft.user, league=league).bid))
            return render(request, 'fantasy_draft/league_detail.html', {
                'league': league,
                'draft_data': draft_data,
            })
        else:
            # Still 'COM' status, but there weren't any bids and results haven't been released
            return render(request, 'fantasy_draft/league_detail.html', {'league': league})
            
    # Standard view ('PRE' phase)
    max_user_ct = league.tournament.player_set.count() // league.number_of_picks
    if request.user.is_authenticated() and request.user.is_active:
        in_league = Order.objects.filter(user=request.user) \
                .filter(league=league).count() > 0
    else:
        in_league = False
        
    return render(request, 'fantasy_draft/league_detail.html', {
        'invite_sent': True if invite_sent == 't' else False,
        'league': league,
        'max_user_ct': max_user_ct,
        'in_league': in_league,
    })
    
def select_player(request, draft_id, player_id):
    if not request.user.is_authenticated() or not request.user.is_active or request.method != "POST":
        # Weird. This shouldn't ever be happening
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
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
    if not request.user.is_authenticated() or not request.user.is_active or request.method != "POST":
        # This should not be happening
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
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
    if not request.user.is_authenticated() or not request.user.is_active or request.method != "POST":
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
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
                last_pick.bid = 0 # last pick automatically bids 0. Good deal, huh?
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
            user_set = UserProfile.objects.filter(username__icontains=name_input)
            user_set = user_set.extra(select={'length': 'Length(username)'}).order_by('length')
            tournament = get_object_or_404(League, pk=league_id).tournament
            
            # Exclude users that already have a league for this tournament
            for u in user_set:
                exclude = False
                if Invitation.objects.filter(recipient=u).filter(sender=request.user).filter(status="UNA"):
                    exclude = True
                else:
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
            player_set = league.tournament.player_set.filter(tag__icontains=tag_input)
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
    if not request.user.is_authenticated() or not request.user.is_active or request.method != "POST":
        # Someone's trying to game the system...
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
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
    if not request.user.is_authenticated() or not request.user.is_active or request.method != "POST":
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
    else:
        invitation = get_object_or_404(Invitation, pk=i_id)
        invitation.status = "ACC"
        invitation.save()
        
        Order.objects.create(number=invitation.league.userprofile_set.count(), 
                user=request.user, league=invitation.league)
                
        # Check if the league is now full
        max_user_ct = invitation.league.tournament.player_set.count() \
                // invitation.league.number_of_picks
        if invitation.league.userprofile_set.count() >= max_user_ct:
            # It is, so we'll cancel all outstanding invitations
            Invitation.objects.filter(league=invitation.league) \
                    .filter(status='UNA') \
                    .delete()
        
        return HttpResponseRedirect('/league/f/' + str(invitation.league.id))
    
def decline(request, i_id):
    if not request.user.is_authenticated() or not request.user.is_active or request.method != "POST":
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
    else:
        invitation = get_object_or_404(Invitation, pk=i_id)
        invitation.delete()
        
        return HttpResponseRedirect(request.GET.get('next', '/'))
        
def activate(request, league_id):
    """Lock users in and create empty drafts for them."""
    league = get_object_or_404(League, pk=league_id)
    if not request.user.is_authenticated() or not request.user.is_active or request.user != league.creator:
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
                user_order.is_turn = (selected_num == 0) # give the turn to the first user
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
        
def leave(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    if request.user.is_authenticated() and request.user.is_active:
        # Remove request.user from the league
        Order.objects.get(user=request.user, league=league).delete()
    return HttpResponseRedirect('/league/f/' + str(league.id))

def player_rankings(request):
    player_scores = defaultdict(int) # {player: score}
    player_tourn_ct = defaultdict(int) # {player: num_tournaments}
    
    date_now = date.today()
    date_1yr_ago = date_now - timedelta(days=365)
    
    # Calculate rankings based on tournaments from the past year
    """ 
    Calculation:
    Average the scores of players over every season tournament that they attend,
    and then apply a multiplicative "activity bonus" to that result.
    
    score_avg = AVG(SCORE(placing) for tournament in tournaments)
    score_final = ACTIVITY BONUS (1.# tournaments attended) * score_avg
    """
    tournaments = Tournament.objects.filter(date__gt=date_1yr_ago).all()
    if not tournaments:
        date_1yr_ago = date(2016, 1, 15) # keep our public range accurate
        tournaments = Tournament.objects.all() # start from the Genesis
    
    for tournament in tournaments:
        for result in tournament.result_set.all():
            player_scores[result.player] += get_score(result.placing)
            player_tourn_ct[result.player] += 1
            
    for player, score in player_scores.items():
        num_tournaments = player_tourn_ct[player]
        score_avg = float(score) / num_tournaments
        
        # Assumption: no more than 9 ranked tournaments per year
        activity_bonus = float(num_tournaments)
        while activity_bonus >= 1.0:
            activity_bonus /= 10
        activity_bonus += 1.0
        
        player_scores[player] = round(score_avg * activity_bonus, 2) # score_final
            
    sorted_ps = sorted(player_scores.items(), key=operator.itemgetter(1), reverse=True)
    # ^ ps = player scores
    
    context = {
        'date_now': date_now, 
        'date_1yr_ago': date_1yr_ago,
        'sorted_ps': sorted_ps,
    }
    return render(request, 'fantasy_draft/player_rankings.html', context)
    
def create_league(request, t_id):
    tournament = get_object_or_404(Tournament, pk=t_id)
    
    if request.user.is_authenticated() and request.user.is_active \
            and date.today() - timedelta(1) < tournament.date \
            and not request.user.leagues.filter(tournament__id=t_id):
        if request.method == 'POST':
            league_form = LeagueForm(data=request.POST)
            if league_form.is_valid():
                # Create a new league and save it
                league = league_form.save(commit=False)
                league.creator = request.user
                league.tournament = tournament
                league.date_created = datetime.now()
                league.save()
                
                # Then add it to the user's collection of leagues
                Order.objects.create(number=0, user=request.user, 
                        league=league, is_turn=True)
                
                # Redirect
                return HttpResponseRedirect(reverse('fantasy_draft:leagues'))
            else:
                error_msg = league_form.errors.as_text()
                
                return render(request, 'fantasy_draft/create_league.html', {
                    'league_form': league_form,
                    't_id': t_id,
                    't_name': tournament.name,
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
    if request.user.is_authenticated() and request.user.is_active:
        tournaments, user_leagues = Tournament.objects.all(), request.user.leagues
        tournament_leagues = []
    
        # Fill in tournament_leagues (a list of tournaments and their corresponding leagues)
        for t in tournaments:
            user_tleague = user_leagues.filter(tournament__name=t.name).first()
            is_ready = t.player_set.count() > 0
            
            if t.date < date(year=2016, month=7, day=1):
                season_desc = "[ 2016 Season 1 ]"
            elif t.date < date(year=2017, month=1, day=1):
                season_desc = "[ 2016 Season 2 ]"
            else:
                season_desc = "Season Unknown"
            
            if user_tleague is None:
                tournament_leagues.append((t, None, season_desc, is_ready))
            else:
                tournament_leagues.append((t, user_tleague, season_desc, is_ready))
    
        context = {
            'tournament_leagues': tournament_leagues, 
            'today_adj': date.today() - timedelta(1), # today "adjusted"
        }
        return render(request, 'fantasy_draft/leagues.html', context)
    else:
        return render(request, 'fantasy_draft/leagues.html', {})
    
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
    else:
        error_code = request.GET.get('e')
        if not error_code:
            return render(request, 'fantasy_draft/login.html', {})
        elif error_code == '1':
            # EC 1 = incorrect login
            return render(request, 'fantasy_draft/login.html', {
                'error_msg': "That's not right! Did you forget your password?",
            })
        elif error_code == '2':
            # EC 2 = activation key has expired
            return render(request, 'fantasy_draft/login.html', {
                'error_msg': "Your activation key has expired. Please re-register.",
            })
    
def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('fantasy_draft:index'))
    elif request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save() # save the new user to the database
            
            # Set the activation key and save it to the user
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            user.activation_key = hashlib.sha1((salt + user.email).encode('utf-8')).hexdigest()
            user.key_expires = datetime.today() + timedelta(20)
            user.save()
            
            # Send email with the activation key
            email_subject = 'Account confirmation'
            email_body = "Hey %s,<br><br>Thanks for signing up! To activate your account, click this link within " % (user.username) \
                    + "480 hours: http://fantasy-ssbm.elasticbeanstalk.com/confirm/%s.<br><br>All the best,<br>Fantasy SSBM" % (user.activation_key)
            msg = EmailMessage(email_subject, email_body, 'Fantasy SSBM <fantasy.ssbm@gmail.com>', [user.email])
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            
            # Log the user in
            user = authenticate(username=request.POST['username'],
                    password=request.POST['password'])
            auth.login(request, user)
            return HttpResponseRedirect('/?m=2')
        else:
            error_msg = user_form.errors.as_text()
            if 'username' in error_msg and 'email' in error_msg and 'password' in error_msg:
                error_msg = 'Invalid username, email, and password.'
            elif 'username' in error_msg and 'email' in error_msg:
                error_msg = 'Invalid username and email.'
            elif 'username' in error_msg and 'password' in error_msg:
                error_msg = 'Invalid username and password.'
            elif 'email' in error_msg and 'password' in error_msg:
                error_msg = 'Invalid email and password.'
            elif 'username' in error_msg and 'required' in error_msg:
                error_msg = 'You must enter a username.'
            elif 'email' in error_msg and 'required' in error_msg:
                error_msg = 'You must enter an email.'
            elif 'password' in error_msg and 'required' in error_msg:
                error_msg = 'You must enter a password.'
            else:
                # Cut the asterisk label out of the error message
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
        
def confirm_registration(request, activation_key):
    # Grab the user who matches the activation key
    user = get_object_or_404(UserProfile, activation_key=activation_key)

    if user.key_expires < timezone.now():
        return HttpResponseRedirect('/login?e=2') # activation failure (error code 2)
    
    user.is_active = True # activate the user
    user.save()
    
    # Log the user in
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth.login(request, user)
    return HttpResponseRedirect('/?m=1')
    
def info(request):
    return render(request, 'fantasy_draft/info.html', {})
    
def profile(request):
    if request.user.is_authenticated() and request.user.is_active:
        league_data = [] # (league, results_published) pairs
        
        for league in request.user.leagues.all():
            results_exist = Result.objects.filter(tournament=league.tournament)
            league_data.append((league, True if results_exist else False))

        context = {'user': request.user, 'league_data': league_data}
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
            return HttpResponseRedirect('/login?e=1') # incorrect login (error code 1)
    else:
        return HttpResponseRedirect('/login?e=1')
                
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))
