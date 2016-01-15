from django.core.management.base import BaseCommand
from ...models import Player, Tournament

import re
import requests
import json
import datetime
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Scrapes the Smash.gg site for tournament entrants'
    
    def handle(self, *args, **options):
        # Tournament creation
        genesis3 = Tournament.objects.filter(name="Genesis 3")
        if not genesis3:
            genesis3 = Tournament.objects.create(name="Genesis 3", date=datetime.date(2016, 1, 15))
        else:
            genesis3 = genesis3[0]
        
        # Scraping
        BASE_URL = 'https://smash.gg/tournament/genesis-3/attendees?per_page=50&filter=%7B%22eventIds%22%3A10617%7D&page='
        PATTERN_A = '"attendee":(\{.*\}\})\},"RankingIterationStore"'
        PATTERN_B = '"attendee":(\{.*\}\})\}\}\},"plugins"'
        
        for i in range(1, 38):
            self.stdout.write('Scraping page ' + str(i) + '...')
            
            page = requests.get(BASE_URL + str(i))
            soup = BeautifulSoup(page.content, "lxml")
            
            script_contents = soup('script', attrs={
                'type': None, 
                'src': None,
            })[0] # we want the first script without a 'type' attribute
            
            match = re.search(PATTERN_A, str(script_contents))
            try:
                attendees = json.loads(match.group(1))
            except AttributeError:
                match = re.search(PATTERN_B, str(script_contents))
                attendees = json.loads(match.group(1))
              
            for player_wrapper in attendees.values():
                player = player_wrapper['player']
                name = player['name']
                if not name: # for some reason they put crews in the attendee listings
                    continue
                
                prefix, tag = player['prefix'], player['gamerTag']
                if prefix:
                    tag = prefix + ' | ' + tag
                
                # Create the player and save him/her to the database
                p = Player.objects.filter(tag=tag)
                if not p:
                    p = Player.objects.create(name=name, tag=tag)
                else:
                    p = p[0]
                p.tournaments.add(genesis3)
                p.save()
