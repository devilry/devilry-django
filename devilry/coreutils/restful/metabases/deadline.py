class DeadlineExtjsModelMeta:
    """ Metadata for Deadline javascript. """
    combobox_fieldgroups = ['assignment', 'period', 'subject',
                            'assignment_group', 'assignment_group_users']
    combobox_tpl = ('<section class="popuplistitem">'
                    '    <table>'
                    '        <tr>'
                    '            <td>'
                    '               <h1>Deadline: {deadline:date}</h1>'
                    '               <ul class="useridlist"><tpl for="assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>'
                    '               <p><tpl if="assignment_group__name"> &ndash; {assignment_group__name}</tpl><p>'
                    '            </td>'
                    '            <td class="rightaligned">'
                    '               <h1>{assignment_group__parentnode__parentnode__parentnode__long_name:ellipsis(60)}</h1>'
                    '               <h2>{assignment_group__parentnode__parentnode__long_name:ellipsis(60)}</h2>'
                    '               <h3>{assignment_group__parentnode__long_name:ellipsis(60)}</h3>'
                    '            </td>'
                    '        </tr>'
                    '    </table>'
                   '</section>')
    combobox_displayfield = 'id'
