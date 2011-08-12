class AssignmentExtjsModelMeta:
    """ Metadata for Assignment javascript. """
    combobox_fieldgroups = ['subject', 'period']
    combobox_tpl = ('<div class="important">{parentnode__parentnode__short_name}.{parentnode__short_name}.{short_name}</div>'
                    '<div class="unimportant">{long_name}</div>')
    combobox_tpl = ('<section class="popuplistitem">'
                    '    <h1>{parentnode__parentnode__long_name}</h1>'
                    '    <h2>{parentnode__long_name}</h2>'
                    '    <h3>{long_name}</h3>'
                   '</section>')
    combobox_displayfield = 'short_name'
