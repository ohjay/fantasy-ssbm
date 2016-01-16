from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

import datetime

class Tournament(models.Model):
    name = models.CharField(max_length=20)
    date = models.DateField()
    
    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return u'%s' % self.name

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
    
    # Only used if the league follows snake order
    ascending = models.BooleanField(default=True)
    
    name = models.CharField(max_length=30) # a name for this league (could be anything)
    date_created = models.DateTimeField()
    tournament = models.ForeignKey(Tournament)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='leagues_created')
    
    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return u'%s' % self.name
    
class Player(models.Model):
    name = models.CharField(max_length=30) # the player's real name (ex. "Dan Rodriguez")
    tag = models.CharField(max_length=30) # the player's gamer tag (ex. "ROOT | ChuDat")
    tournaments = models.ManyToManyField(Tournament, blank=True)
    
    def __str__(self):
        return self.tag
        
    def __unicode__(self):
        return u'%s' % self.tag
        
class Draft(models.Model):
    league = models.ForeignKey(League) # each draft belongs to a league
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    ) # the user associated with this draft
    players = models.ManyToManyField(Player, blank=True) # the players in the draft
    
    def __str__(self):
        return str(self.user) + "'s " + str(self.league.tournament) + ' draft'
        
    def __unicode__(self):
        return u"%s's %s draft" % (str(self.user), str(self.league.tournament))
        
class Result(models.Model):
    placing = models.IntegerField()
    player = models.ForeignKey(Player)
    tournament = models.ForeignKey(Tournament)
    
    def __str__(self):
        return self.player.tag + ' (' + str(self.placing) + ')'
    
    def __unicode__(self):
        return u'%s (%s)' % (self.player.tag, self.placing)
        
class Order(models.Model):
    number = models.PositiveSmallIntegerField()
    is_turn = models.BooleanField(default=False)
    
    # Only used if users bid for order
    is_final = models.BooleanField(default=False) # describes whether the ordering position is final
    bid = models.IntegerField(default=0) # -1 signifies that the user has dropped out for the round
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    league = models.ForeignKey(League)
    
    def __str__(self):
        return str(self.user) + "'s order for league " + str(self.league)
    
    def __unicode__(self):
        return u"%s's order for league %s" % (str(self.user), str(self.league))
    
class UserProfile(AbstractUser):
    leagues = models.ManyToManyField(League, through='Order', blank=True)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username
        
    def __unicode__(self):
        return u'%s' % self.username
        
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
    
    def __str__(self):
        return '%s invitation from %s to %s' % (str(self.league), str(self.sender), str(self.recipient))
    
    def __unicode__(self):
        return u'%s invitation from %s to %s' % (str(self.league), str(self.sender), str(self.recipient))
