/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('devilry_subjectadmin.view.managestudents.ManageStudentsOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.managestudentsoverview',
    cls: 'devilry_subjectadmin_managestudentsoverview',
    requires: [
        'devilry_subjectadmin.view.managestudents.HelpPanel',
        'devilry_subjectadmin.view.managestudents.ListOfGroups',
        'devilry_subjectadmin.view.managestudents.NoGroupSelectedView',
        'devilry_subjectadmin.view.managestudents.SingleGroupSelectedView',
        'devilry_subjectadmin.view.managestudents.MultipleGroupsSelectedView'
    ],


    /**
     * @cfg {String} [assignment_id] (required)
     */

    /**
     * @cfg {String} [select_groupids_on_load] (optional)
     * String containing a comma-separated list of group-ids that should be selected on load.
     */

    /**
     * @cfg {String} [select_delivery_on_load] (optional)
     * A string containing the ID of a delivery to select on load.
     * Only used when ``select_groupids_on_load`` contains exactly one ID.
     */

    /**
     * @cfg {Boolean} [add_students_on_load=false] (optional)
     * Should we show the add-students window on load?
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            border: false,
            frame: false,
            style: 'background-color: transparent !important;',
            items: [{
                xtype: 'listofgroups',
                region: 'west',
                border: true,
                frame: false,
                width: 390, // Default width
                minWidth: 260, // Wont be able to make it smaller than this

                // Only resize to the right (east)
                resizable: true,
                resizeHandles: 'e'
            }, {
                xtype: 'container',
                region: 'center',
                itemId: 'body',
                layout: 'card',
                items: [{
                    xtype: 'nogroupselectedview',
                    itemId: 'nogroupsSelected'
                }, {
                    xtype: 'singlegroupview',
                    itemId: 'singlegroupSelected'
                }, {
                    xtype: 'multiplegroupsview',
                    itemId: 'multiplegroupsSelected'
                }]
            }, {
                xtype: 'managestudents_help',
                autoScroll: true,
                title: gettext('Help'),
                bodyPadding: 10,
                region: 'east',
                width: 400,
                collapsible: true,   // make collapsible
                collapsed: true
            }]
        });
        this.callParent(arguments);
    }
});
