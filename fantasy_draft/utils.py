SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def to_ordinal(num):
    """Returns the ordinal representation of NUM + 1.
       Implementation borrowed from http://goo.gl/rxEeM7."""
    if 10 <= num + 1 <= 20: # we know that NUM is less than 100
        return str(num + 1) + 'th'
    return str(num + 1) + SUFFIXES.get((num + 1) % 10, 'th')
    