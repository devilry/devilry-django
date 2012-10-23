Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.CreateDeadlineForm', {
    extend: 'devilry_subjectadmin.view.bulkmanagedeadlines.BaseDeadlineForm',
    alias: 'widget.bulkmanagedeadlines_createdeadlineform',
    extraCls: 'createdeadlineform',

    getItems: function() {
        var items = this.callParent();
        items.push({
            xtype: 'container',
            itemId: 'createmodeContainer',
            hidden: true,
            items: [{
                xtype: 'box',
                margin: '20 0 0 0',
                html: [
                    '<h2>',
                        interpolate(gettext('Add %(deadline_term)s to'), {
                            deadline_term: gettext('deadline')
                        }, true),
                    '</h2>'
                ].join('')
            }, {
                xtype: 'radiogroup',
                anchor: '100%',
                vertical: true,
                columns: 1,
                fieldLabel: interpolate(gettext('Add %(deadline_term)s to'), { // NOTE: We need the fieldLabel for error handling, even though it is hidden below.
                    deadline_term: gettext('deadline')
                }, true),
                hideLabel: true,
                items: [{
                    boxLabel: interpolate(gettext('%(groups_term)s where active %(feedback_term)s is a failing %(grade_term)s.'), {
                        groups_term: gettext('groups'),
                        grade_term: gettext('grade'),
                        feedback_term: gettext('feedback')
                    }, true),
                    name: 'createmode',
                    inputValue: 'failed',
                    cls: 'createmode_failed',
                    checked: true
                }, {
                    boxLabel: interpolate(gettext('%(groups_term)s where active %(feedback_term)s is a failing %(grade_term)s, %(groups_term)s with no %(feedback_term)s and groups with no %(deadlines_term)s.'), {
                        groups_term: gettext('groups'),
                        grade_term: gettext('grade'),
                        feedback_term: gettext('feedback'),
                        deadlines_term: gettext('deadlines')
                    }, true),
                    name: 'createmode',
                    cls: 'createmode_failed_or_no_feedback',
                    inputValue: 'failed-or-no-feedback'
                }, {
                    boxLabel: interpolate(gettext('%(groups_term)s with no %(deadlines_term)s.'), {
                        groups_term: gettext('groups'),
                        deadlines_term: gettext('deadlines')
                    }, true),
                    name: 'createmode',
                    cls: 'createmode_no_deadlines',
                    inputValue: 'no-deadlines'
                }, {
                    boxLabel: interpolate(gettext('specify %(groups_term)s manually.'), {
                        groups_term: gettext('groups')
                    }, true),
                    name: 'createmode',
                    itemId: 'createmodeSpecificGroups',
                    cls: 'createmode_specific_groups',
                    inputValue: 'specific-groups'
                }]
            }, {
                xtype: 'panel',
                itemId: 'createmodeSpecificGroupsSelectpanel',
                layout: 'column',
                margin: '10 0 10 25',
                hidden: true,
                border: 0,
                items: [{
                    xtype: 'bulkmanagedeadlines_allgroupsgrid',
                    columnWidth: 1,
                    height: 300 // Initial height - this is dynamically adjusted to the body-heigth by the controller
                }, {
                    xtype: 'box',
                    width: 250,
                    padding: '0 0 0 20',
                    cls: 'bootstrap',
                    html: [
                        '<p class="muted"><small>',
                            gettext('Select one or more groups. The deadline will only be added to the selected groups.'),
                        '</small></p>'
                    ].join('')
                }]
            }]
        });
        return items;
    }
});
