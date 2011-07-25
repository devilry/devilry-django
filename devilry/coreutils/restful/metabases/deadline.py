class DeadlineExtjsModelMeta:
    """ Metadata for Deadline javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject']
    combobox_tpl = ('<div class="important">{deadline:date}</div>'
                    '<div class="unimportant">'
                        '{assignment_group__parentnode__parentnode__parentnode__short_name}.'
                        '{assignment_group__parentnode__parentnode__short_name}.'
                        '{assignment_group__parentnode__short_name}'
                        '&mdash; Group id: {assignment_group}</div>')
    combobox_displayfield = 'id'
