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
    if placing >= 193: return 60
    elif placing >= 129: return 100
    elif placing >= 97: return 130
    elif placing >= 65: return 160
    elif placing >= 49: return 190
    elif placing >= 33: return 250
    elif placing >= 25: return 280
    elif placing >= 17: return 310
    elif placing >= 13: return 340
    elif placing >= 9: return 370
    elif placing >= 7: return 400
    elif placing >= 5: return 430
    elif placing == 4: return 460
    elif placing == 3: return 490
    elif placing == 2: return 520
    elif placing == 1: return 570
    
