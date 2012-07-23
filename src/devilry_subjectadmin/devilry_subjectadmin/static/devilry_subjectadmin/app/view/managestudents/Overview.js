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
            frame: true,
            items: [{
                xtype: 'listofgroups',
                region: 'west',
                border: true,
                frame: false,
                split: true,
                width: 350
            }, {
                xtype: 'panel',
                region: 'center',
                //border: false,
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
