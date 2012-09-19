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
                message: gettext('Select groups from the list on your left hand side. The help below is always available by clicking on the help-column on your right hand side.')
            }, {
                xtype: 'managestudents_help',
                border: false
            }]
        });
        this.callParent(arguments);
    }
});
