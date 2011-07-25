class AssignmentGroupExtjsModelMeta:
    """ Metadata for AssignmentGroup javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject']
    combobox_tpl = ('<div class="important">Group id: {id}'
                        #'<tpl for="candidates__identifier">, {.}</tpl>'
                    '</div>'
                    '<div class="unimportant">'
                        '{parentnode__parentnode__parentnode__short_name}.'
                        '{parentnode__parentnode__short_name}.'
                        '{parentnode__short_name}</div>')
    combobox_displayfield = 'id'
