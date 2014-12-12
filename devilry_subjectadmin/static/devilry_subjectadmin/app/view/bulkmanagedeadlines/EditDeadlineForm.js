Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.EditDeadlineForm', {
    extend: 'devilry_subjectadmin.view.bulkmanagedeadlines.BaseDeadlineForm',
    alias: 'widget.bulkmanagedeadlines_editdeadlineform',
    extraCls: 'editdeadlineform',

    requires: [
        'devilry_subjectadmin.view.bulkmanagedeadlines.GroupsInDeadlineSelectGrid'
    ],

    /**
     * @cfg {Object} [groupsStore]
     * The store to use for the specify groups grid.
     */

    getItems: function() {
        var items = this.callParent();
        items.push({
            xtype: 'fieldset',
            itemId: 'editSpecificGroupsFieldset',
            cls: 'edit_specific_groups_fieldset',
            layout: 'anchor',
            title: gettext('Only apply these changes to some of the groups in the deadline.'),
            checkboxName: 'editSpecific',
            checkboxToggle: true,
            collapsed: true,
            items: [{
                xtype: 'container',
                anchor: '100%',
                itemId: 'specifyGroupsContainer',
                layout: 'column',
                items: [{
                    xtype: 'bulkmanagedeadlines_groupsindeadlineselectgrid',
                    columnWidth: 1,
                    store: this.groupsStore,
                    height: 300
                }, {
                    xtype: 'box',
                    width: 250,
                    padding: '0 0 0 20',
                    cls: 'bootstrap',
                    html: [
                        '<p class="muted"><small>',
                            gettext('Applying deadline changes to only some groups will effectively split this deadline in two. Remember that groups have individual deadlines and that this view groups deadlines with the same timestamp and text. This means that editing a deadline actually updates a bunch of individual deadlines (one for each group). So when you select only some of the groups within the current deadline, you choose to change only some of the individual deadlines, which appears to split this deadline in two.'),
                        '</small></p>'
                    ].join('')
                }]
            }]
        });
        return items;
    }
});
