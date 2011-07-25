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
