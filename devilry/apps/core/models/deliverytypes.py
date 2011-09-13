ELECTRONIC = 0
NON_ELECTRONIC = 1
ALIAS = 2

def as_choices_tuple():
    return ((ELECTRONIC, 'Electronic'),
            (NON_ELECTRONIC, 'Non electronic'),
            (ALIAS, 'Alias'))
