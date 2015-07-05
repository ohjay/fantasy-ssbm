from django.db import models

class League(models.Model):
    name = models.CharField(max_length=30) # a name for this league (could be anything)
    date_created = models.DateTimeField('date created')
    def __str__(self):
        return self.name
        
class TournamentResult(models.Model):
    player_tag = models.CharField(max_length=30)
    placing = models.IntegerField(max_length=4)
    def __str__(self):
        return self.player_tag + ' (' + str(self.placing) + ')'
        
class Tournament(models.Model):
    name = models.CharField(max_length=20)
    results = models.ManyToManyField(TournamentResult)
    date = models.DateField('tournament date')
    def __str__(self):
        return self.name
    
class Pool(models.Model):
    identifier = models.CharField(max_length = 20)
    def __str__(self):
        return self.identifier
    
class Player(models.Model):
    name = models.CharField(max_length=30) # the player's real name
    tag = models.CharField(max_length=30) # the player's gamer tag (ex. ChuDat)
    pool = models.ForeignKey(Pool)
    placing = models.IntegerField(max_length=4)
    seed = models.IntegerField(max_length=4)
    picture = models.ImageField(upload_to='player_images')
    description = models.TextField()
    tournaments = models.ManyToManyField(Tournament)
    def __str__(self):
        return self.tag
    
class User(models.Model):
    name = models.CharField(max_length=30) # the user's irl name
    
class Draft(models.Model):
    league = models.ForeignKey(League) # there are many drafts for one league
    user = models.ForeignKey(User) # the user associated with this draft
    players = models.ManyToManyField(Player) # the players in the draft
    def __str__(self):
        return self.user + "'s draft in the league " + self.league
