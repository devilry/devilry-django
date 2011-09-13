ELECTRONIC = 0
NON_ELECTRONIC = 1
ALIAS = 2

def as_choices_tuple():
    return (('Electronic', ELECTRONIC),
            ('Non electronic', NON_ELECTRONIC),
            ('Alias', ALIAS))
