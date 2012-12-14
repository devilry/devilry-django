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
            layout: 'anchor',
            items: [{
                xtype: 'box',
                margin: '20 0 0 0',
                html: [
                    '<h2>',
                        gettext('Add deadline to'),
                    '</h2>'
                ].join('')
            }, {
                xtype: 'radiogroup',
                anchor: '100%',
                vertical: true,
                columns: 1,
                fieldLabel: gettext('Add deadline to'), // NOTE: We need the fieldLabel for error handling, even though it is hidden below.
                hideLabel: true,
                items: [{
                    boxLabel: gettext('groups where active feedback is a failing grade.'),
                    name: 'createmode',
                    inputValue: 'failed',
                    cls: 'createmode_failed',
                    checked: true
                }, {
                    boxLabel: gettext('groups where active feedback is a failing grade, groups with no feedback and groups with no deadlines.'),
                    name: 'createmode',
                    cls: 'createmode_failed_or_no_feedback',
                    inputValue: 'failed-or-no-feedback'
                }, {
                    boxLabel: gettext('groups with no deadlines.'),
                    name: 'createmode',
                    cls: 'createmode_no_deadlines',
                    inputValue: 'no-deadlines'
                }, {
                    boxLabel: gettext('specify groups manually.'),
                    name: 'createmode',
                    itemId: 'createmodeSpecificGroups',
                    cls: 'createmode_specific_groups',
                    inputValue: 'specific-groups'
                }]
            }, {
                xtype: 'panel',
                itemId: 'createmodeSpecificGroupsSelectpanel',
                layout: 'column',
                anchor: '100%',
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
