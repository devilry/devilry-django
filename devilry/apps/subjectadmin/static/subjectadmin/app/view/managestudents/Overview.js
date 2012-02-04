/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('subjectadmin.view.managestudents.Overview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.managestudentsoverview',
    cls: 'managestudentsoverview sidebarlayout',
    requires: [
    ],


    /**
     * @cfg {String} subject_shortname (required)
     */

    /**
     * @cfg {String} period_shortname (required)
     */

    /**
     * @cfg {String} assignment_shortname (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            frame: false,

            items: [{
                xtype: 'box',
                html: 'hei'
            }]
        });
        this.callParent(arguments);
    }
});
