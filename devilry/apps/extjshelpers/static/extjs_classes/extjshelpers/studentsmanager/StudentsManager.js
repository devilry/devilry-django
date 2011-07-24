Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid'
    ],
    layout: 'border',

    config: {
        assignmentgroupstore: undefined
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
                title: 'Center Region',
                region: 'center',     // center region is required, no width/height specified
                //xtype: 'studentsmanager_studentsgrid',
                xtype: 'panel',
                layout: 'fit',
                margins: '5 5 0 0',
                items: []
            }],

        });
        this.callParent(arguments);
    }
});
