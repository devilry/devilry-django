class DeliveryExtjsModelMeta:
    """ Metadata for Delivery javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject', 'deadline',
                            'assignment_group', 'assignment_group_users']
    combobox_tpl = ('<div class="section popuplistitem">'
                    '   <p class="path">'
                           '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.'
                           '{deadline__assignment_group__parentnode__parentnode__short_name}.'
                           '{deadline__assignment_group__parentnode__short_name}'
                    '   </p>'
                    '   <tpl if="!is_student">'
                    '       <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>'
                    '   </tpl>'
                    '   <tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>'
                    '   <div class="section dl_valueimportant">'
                    '      <div class="section">'
                    '          <h1>Delivery number</h1>'
                    '          {number}'
                    '      </div>'
                    '   </div>'
                    '</div>')
    combobox_displayfield = 'id'
