class DeliveryExtjsModelMeta:
    """ Metadata for Delivery javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject', 'deadline',
                            'assignment_group', 'assignment_group_users']
    combobox_tpl = ('<section class="popuplistitem">'
                    '    <table>'
                    '        <tr>'
                    '            <td>'
                    '               <h1>Deadline: {deadline__deadline:date}</h1>'
                    '               <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>'
                    '               <p>Delivery: {number}<tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl><p>'
                    '            </td>'
                    '            <td class="rightaligned">'
                    '               <h1>{deadline__assignment_group__parentnode__parentnode__parentnode__long_name:ellipsis(60)}</h1>'
                    '               <h2>{deadline__assignment_group__parentnode__parentnode__long_name:ellipsis(60)}</h2>'
                    '               <h3>{deadline__assignment_group__parentnode__long_name:ellipsis(60)}</h3>'
                    '            </td>'
                    '        </tr>'
                    '    </table>'
                   '</section>')
    combobox_displayfield = 'id'
