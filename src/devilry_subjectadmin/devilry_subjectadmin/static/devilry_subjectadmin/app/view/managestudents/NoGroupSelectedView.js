/**
 * A panel that displays information when no group is selected.
 */
Ext.define('devilry_subjectadmin.view.managestudents.NoGroupSelectedView' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.nogroupselectedview',
    cls: 'nogroupselectedview bootstrap',
    requires: [
        'devilry_subjectadmin.view.managestudents.HelpPanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            padding: 20,
            autoScroll: true,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'alertmessage',
                type: 'info',
                message: interpolate(gettext('%(Students_term)s are in a group even when they work alone. That means that the list to your left is the groups registered on this assignment. Choose one or more %(groups_term)s to gain access to settings, such as %(examiners_term)s and %(tags_term)s.'), {
                    Students_term: gettext('Students'),
                    groups_term: gettext('groups'),
                    examiners_term: gettext('examiners'),
                    tags_term: gettext('tags')
                }, true)
            }, {
                xtype: 'managestudents_help',
                border: false
            }]
        });
        this.callParent(arguments);
    }
});
