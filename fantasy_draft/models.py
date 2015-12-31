from django.db import models
from django.contrib.auth.models import User

class Tournament(models.Model):
    name = models.CharField(max_length=20)
    date = models.DateField()
    def __str__(self):
        return self.name

class League(models.Model):
    name = models.CharField(max_length=30) # a name for this league (could be anything)
    date_created = models.DateTimeField()
    tournament = models.OneToOneField(Tournament)
    users = models.ManyToManyField(User, blank=True)
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
    user = models.ForeignKey(User) # the user associated with this draft
    players = models.ManyToManyField(Player, blank=True) # the players in the draft
    def __str__(self):
        return self.user + "'s " + self.league.tournament + ' draft'
        
class Result(models.Model):
    placing = models.IntegerField()
    player = models.ForeignKey(User)
    tournament = models.ForeignKey(Tournament)
    def __str__(self):
        return self.player.tag + ' (' + str(self.placing) + ')'
