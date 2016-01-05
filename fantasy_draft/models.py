from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Tournament(models.Model):
    name = models.CharField(max_length=20)
    date = models.DateField()
    
    def __str__(self):
        return self.name

class League(models.Model):
    PHASES = (
        ('PRE', 'Phase 1: Preliminary'), # users can still join/leave the league
        ('BID', 'Phase 2: Bidding'), # users are locked in and are now bidding for order
        ('SEL', 'Phase 3: Selection'), # users should be selecting players for their drafts
        ('COM', 'Phase 4: Complete'), # all draft picks have now been made
    )
    phase = models.CharField(max_length=3, choices=PHASES, default='PRE')
    
    # Options selected by the creator:
    random_order = models.BooleanField(default=False) # order is either random or determined by bidding
    snake_style = models.BooleanField(default=False) # snake style or cyclic sequential
    number_of_picks = models.PositiveSmallIntegerField()
    
    name = models.CharField(max_length=30) # a name for this league (could be anything)
    date_created = models.DateTimeField()
    tournament = models.ForeignKey(Tournament)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    def __str__(self):
        return self.name
    
class Player(models.Model):
    name = models.CharField(max_length=30) # the player's real name (ex. "Dan Rodriguez")
    tag = models.CharField(max_length=30) # the player's gamer tag (ex. "ROOT | ChuDat")
    tournaments = models.ManyToManyField(Tournament, blank=True)
    
    def __str__(self):
        return self.tag
        
class Draft(models.Model):
    league = models.ForeignKey(League) # each draft belongs to a league
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    ) # the user associated with this draft
    players = models.ManyToManyField(Player, blank=True) # the players in the draft
    
    def __str__(self):
        return str(self.user) + "'s " + str(self.league.tournament) + ' draft'
        
class Result(models.Model):
    placing = models.IntegerField()
    player = models.ForeignKey(Player)
    tournament = models.ForeignKey(Tournament)
    
    def __str__(self):
        return self.player.tag + ' (' + str(self.placing) + ')'
        
class Order(models.Model):
    number = models.PositiveSmallIntegerField()
    
    # Only used if users bid for order
    is_final = models.BooleanField(default=False) # describes whether the ordering position is final
    bid = models.PositiveIntegerField(null=True, blank=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    league = models.ForeignKey(League)
    
class UserProfile(AbstractUser):
    leagues = models.ManyToManyField(League, through='Order', blank=True)
    
    def __str__(self):
        return self.username
        
class Invitation(models.Model):
    """An invitation to join a league."""
    league = models.ForeignKey(League)
    date_issued = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='invites_sent')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='invites_received')
    
    STATUS_CODES = (
        ('UNA', 'unanswered'),
        ('ACC', 'accepted'),
        ('DEC', 'declined'),
    )
    status = models.CharField(max_length=3, choices=STATUS_CODES, default='UNA')
