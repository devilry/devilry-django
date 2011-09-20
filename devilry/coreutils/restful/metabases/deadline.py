class DeadlineExtjsModelMeta:
    """ Metadata for Deadline javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject',
                            'assignment_group', 'assignment_group_users']
    combobox_tpl = ('<div class="section popuplistitem">'
                    '   <p class="path">'
                           '{assignment_group__parentnode__parentnode__parentnode__short_name}.'
                           '{assignment_group__parentnode__parentnode__short_name}.'
                           '{assignment_group__parentnode__short_name}'
                    '   </p>'
                    '   <tpl if="!is_student">'
                    '       <ul class="useridlist"><tpl for="assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>'
                    '   </tpl>'
                    '   <h1>{deadline:date}</h1>'
                    '   <p><tpl if="assignment_group__name"> &ndash; {assignment_group__name}</tpl><p>'
                    '   <div class="section dl_valueimportant">'
                    '       <div class="section">'
                    '           <h1>Deliveries</h1>'
                    '           {number_of_deliveries}'
                    '       </div>'
                    '   </div>'
                   '</div>')
    combobox_displayfield = 'id'
