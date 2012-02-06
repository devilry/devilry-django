/**
 * Manage students overview (overview of all students on an assignment).
 */
Ext.define('subjectadmin.view.managestudents.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.managestudentsoverview',
    cls: 'managestudentsoverview sidebarlayout',
    requires: [
        'subjectadmin.view.managestudents.ListOfGroups'
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
            layout: 'border',
            frame: false,
            tbar: [{
                xtype: 'button',
                itemId: 'addstudents',
                text: dtranslate('subjectadmin.managestudents.addstudents')
            }],
            items: [{
                xtype: 'listofgroups',
                region: 'west',
                //border: false,
                width: 350
            }, {
                xtype: 'panel',
                region: 'center',
                border: false,
                //ui: 'transparentpanel',
                bodyPadding: 20,
                items: {
                    xtype: 'box',
                    html: 'TODO'
                }
            }]
        });
        this.callParent(arguments);
    }
});
