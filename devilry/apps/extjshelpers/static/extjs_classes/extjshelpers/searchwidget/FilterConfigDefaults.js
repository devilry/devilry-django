/** 
 * Defaults for {@link devilry.extjshelpers.searchwidget.SearchResults#filterconfig}
 * for student, administrator and examiner.
 */
Ext.define('devilry.extjshelpers.searchwidget.FilterConfigDefaults', {
    statics: {
        assignment: {
            type: 'assignment'
        },
        assignmentgroup: {
            type: 'group',
            shortcuts: {
                assignment: 'parentnode'
            }
        },
        deadline: {
            type: 'deadline',
            shortcuts: {
                assignment: 'assignment_group__parentnode',
                group: 'assignment_group',
            }
        },
        delivery: {
            type: 'delivery',
            shortcuts: {
                assignment: 'deadline__assignment_group__parentnode',
                group: 'deadline__assignment_group'
            }
        }
    }
});
