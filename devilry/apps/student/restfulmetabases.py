class AssignmentExtjsModelMeta:
    """ Metadata for Assignment javascript. """
    combobox_fieldgroups = ['subject', 'period']
    combobox_tpl = ('<div class="important">{parentnode__parentnode__short_name}.{parentnode__short_name}.{short_name}</div>'
                    '<div class="unimportant">{long_name}</div>')
    combobox_displayfield = 'short_name'

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


class DeliveryExtjsModelMeta:
    """ Metadata for Delivery javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject',
                            'assignment_group']
    combobox_tpl = ('<div class="important">Delivery: {number} '
                        '<tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>'
                        #'<tpl for="deadline__assignment_group__candidates__identifier">, {.}</tpl>'
                    '</div>'
                    '<div class="unimportant">'
                        '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.'
                        '{deadline__assignment_group__parentnode__parentnode__short_name}.'
                        '{deadline__assignment_group__parentnode__short_name} '
                        '&mdash; Group id: {deadline__assignment_group}</div>')
    combobox_displayfield = 'id'
