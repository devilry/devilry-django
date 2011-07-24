Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    cls: 'studentsmanager',
    layout: 'border',

    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid'
    ],

    config: {
        assignmentgroupstore: undefined,
        assignmentid: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                region: 'north',     // position for region
                xtype: 'panel',
                height: 100
            },{
                region:'west',
                xtype: 'panel',
                width: 200,
                layout: 'fit',
                tbar: [{
                    xtype: 'button',
                    text: 'Add more students',
                    iconCls: 'icon-add-32',
                    scale: 'large'
                }],
                items: [{
                    xtype: 'studentsmanager_filterselector'
                }]
            },{
                region: 'center',     // center region is required, no width/height specified
                xtype: 'panel',
                layout: 'fit',
                items: [{
                    xtype: 'studentsmanager_studentsgrid',
                    store: this.assignmentgroupstore,
                    assignmentid: this.assignmentid
                }]
            }],

        });
        this.callParent(arguments);
    }
});
