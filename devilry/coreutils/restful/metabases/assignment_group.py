class AssignmentGroupExtjsModelMeta:
    """ Metadata for AssignmentGroup javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject', 'users']
    combobox_tpl = ('<div class="section popuplistitem">'
                    '   <p class="path">'
                           '{parentnode__parentnode__parentnode__short_name:ellipsis(60)}.'
                           '{parentnode__parentnode__short_name:ellipsis(60)}.'
                           '{parentnode__short_name:ellipsis(60)}'
                    '   </p>'
                    '   <tpl if="!is_student">'
                    '       <h1><ul class="useridlist"><tpl for="candidates__identifier"><li>{.}</li></tpl></ul></h1>'
                    '   </tpl>'
                    '   <p><tpl if="name">{name}</tpl><p>'
                   '</div>')
    combobox_displayfield = 'id'
