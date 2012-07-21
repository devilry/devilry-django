/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('devilry_subjectadmin.view.managestudents.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudentsoverview',
    cls: 'managestudentsoverview sidebarlayout',
    requires: [
        'devilry_subjectadmin.view.managestudents.ListOfGroups'
    ],


    /**
     * @cfg {String} assignment_id (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            frame: false,
            items: [{
                xtype: 'listofgroups',
                //margin: '10 0 10 40',
                region: 'west',
                //border: false,
                resizable: true,
                width: 300,
            }, {
                xtype: 'panel',
                region: 'center',
                //margin: '10 40 10 20',
                padding: '0 0 0 20',
                border: false,
                layout: 'fit',
                itemId: 'body'
            }],

            bbar: [{
                xtype: 'autocompletegroupwidget',
                flex: 1,
                hideTrigger: true,
                itemId: 'selectUsersByAutocompleteWidget'
            }]
        });
        this.callParent(arguments);
    }
});
