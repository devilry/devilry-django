Ext.define('devilry.statistics.ScalePointsPanel', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-scalepointspanel',
    
    initComponent: function() {
        Ext.apply(this, {
            selType: 'cellmodel',
            plugins: [
                Ext.create('Ext.grid.plugin.CellEditing', {
                    clicksToEdit: 1
                })
            ],

            columns: [{
                header: 'Long name',
                dataIndex: 'long_name',
                flex: 1
            }, {
                header: 'Scale by (percent)',
                dataIndex: 'scale_points_percent',
                width: 110,
                field: {
                    xtype: 'numberfield',
                    allowBlank: false
                }
            }],

            listeners: {
                scope: this,
                edit: function(editor, e) {
                    e.record.commit();
                    e.record.save();
                }
            }
        });
        this.callParent(arguments);
    }
});
