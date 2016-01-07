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
    