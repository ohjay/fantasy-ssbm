from datetime import date

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def to_ordinal(num):
    """Returns the ordinal representation of NUM + 1.
       Implementation borrowed from http://goo.gl/rxEeM7."""
    if 10 <= num + 1 <= 20: # we know that NUM is less than 100
        return str(num + 1) + 'th'
    return str(num + 1) + SUFFIXES.get((num + 1) % 10, 'th')
    
def handle_completion(draft):
    """If the league is complete, switches phases and returns True."""
    if draft.players.count() < draft.league.number_of_picks:
        return False
        
    draft.league.phase = 'COM' # the selection phase is over
    draft.league.save()
    return True
    
def get_score(placing):
    """Returns a point score based on the given placing."""
    if placing >= 513: return 0
    elif placing >= 385: return 10
    elif placing >= 257: return 30
    elif placing >= 193: return 50
    elif placing >= 129: return 75
    elif placing >= 97: return 100
    elif placing >= 65: return 130
    elif placing >= 49: return 160
    elif placing >= 33: return 195
    elif placing >= 25: return 230
    elif placing >= 17: return 270
    elif placing >= 13: return 310
    elif placing >= 9: return 355
    elif placing >= 7: return 400
    elif placing >= 5: return 450
    elif placing == 4: return 500
    elif placing == 3: return 555
    elif placing == 2: return 610
    elif placing == 1: return 670
    
TOURNAMENT_SCHEDULE = [
    ('Pound 2016', date(2016, 4, 2)),
    ('EGLX', date(2016, 4, 29)),
    ('DreamHack Austin', date(2016, 5, 6)),
    ('CEO 2016', date(2016, 6, 24)),
    ('EVO 2016', date(2016, 7, 15)),
    ('Super Smash Con', date(2016, 8, 11)),
    ('The Big House 6', date(2016, 10, 7)),
    ('DreamHack Winter', date(2016, 11, 24)),
]
