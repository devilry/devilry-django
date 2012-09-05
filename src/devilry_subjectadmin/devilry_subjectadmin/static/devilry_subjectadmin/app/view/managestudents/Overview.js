/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('devilry_subjectadmin.view.managestudents.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudentsoverview',
    cls: 'devilry_subjectadmin_managestudentsoverview',
    requires: [
        'devilry_subjectadmin.view.managestudents.ListOfGroups'
    ],


    /**
     * @cfg {String} [assignment_id] (required)
     */

    /**
     * @cfg {String} [select_groupids_on_load] (optional)
     * String containing a comma-separated list of group-ids that should be selected on load.
     */

    /**
     * @cfg {Boolean} [add_students_on_load=false] (optional)
     * Should we show the add-students window on load?
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            frame: false,
            items: [{
                xtype: 'listofgroups',
                region: 'west',
                border: true,
                frame: true,
                width: 350, // Default width
                minWidth: 350, // Wont be able to make it smaller than this

                // Only resize to the right (east)
                resizable: true,
                resizeHandles: 'e'
            }, {
                xtype: 'panel',
                region: 'center',
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
