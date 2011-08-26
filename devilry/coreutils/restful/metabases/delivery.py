class DeliveryExtjsModelMeta:
    """ Metadata for Delivery javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject', 'deadline',
                            'assignment_group', 'assignment_group_users']
    combobox_tpl = ('<section class="popuplistitem">'
                    '    <p class="path">'
                            '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.'
                            '{deadline__assignment_group__parentnode__parentnode__short_name}.'
                            '{deadline__assignment_group__parentnode__short_name}'
                    '    </p>'
                    '    <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>'
                    '    <section class="dl_valueimportant">'
                    '       <section>'
                    '           <h1>Delivery number</h1>'
                    '           {number}<tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>'
                    '       </section>'
                    '    </section>'
                    '</section>')
    combobox_displayfield = 'id'
