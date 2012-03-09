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
            items: [{
                xtype: 'listofgroups',
                margin: {top:10, right: 0, bottom: 10, left: 20},
                region: 'west',
                //border: false,
                width: 350,
                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'top',
                    itemId: 'listofgroupsToolbar',
                    items: [{
                        xtype: 'button',
                        itemId: 'selectall',
                        text: dtranslate('themebase.selectall')
                    }]
                }]
            }, {
                xtype: 'panel',
                region: 'center',
                margin: {top:10, right: 20, bottom: 10, left: 20},
                border: false,
                itemId: 'body'
            }]
        });
        this.callParent(arguments);
    }
});
