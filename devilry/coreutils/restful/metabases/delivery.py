class DeliveryExtjsModelMeta:
    """ Metadata for Delivery javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject',
                            'assignment_group', 'assignment_group_users']
    combobox_tpl = ('<section class="popuplistitem">'
                    #'<div class="important">Delivery: {number} '
                        #'<tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>'
                        #'<tpl for="deadline__assignment_group__candidates__identifier">, {.}</tpl>'
                    #'</div>'
                    '    <table>'
                    '        <tr>'
                    '            <td>'
                    '               <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>'
                    '               <p>Delivery: {number}<tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl><p>'
                    '            </td>'
                    '            <td class="rightaligned">'
                    '               <h1>{deadline__assignment_group__parentnode__parentnode__parentnode__long_name}</h1>'
                    '               <h2>{deadline__assignment_group__parentnode__parentnode__long_name}</h2>'
                    '               <h3>{deadline__assignment_group__parentnode__long_name}</h3>'
                    '            </td>'
                    '        </tr>'
                    '    </table>'
                        #'&mdash; Group id: {deadline__assignment_group}</div>'
                   '</section>')
    combobox_displayfield = 'id'
