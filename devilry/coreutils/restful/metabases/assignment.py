class AssignmentExtjsModelMeta:
    """ Metadata for Assignment javascript. """
    combobox_fieldgroups = ['subject', 'period']
    combobox_tpl = ('<div class="important">{parentnode__parentnode__short_name}.{parentnode__short_name}.{short_name}</div>'
                    '<div class="unimportant">{long_name}</div>')
    combobox_displayfield = 'short_name'
