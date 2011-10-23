Ext.define('devilry.statistics.ScalePointsPanel', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-scalepointspanel',
    requires: [
        'devilry.extjshelpers.HelpWindow'
    ],
    
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
            },

            bbar: [{
                xtype: 'button',
                iconCls: 'icon-help-32',
                text: 'Help',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this._onHelp
                }
            }]
        });
        this.callParent(arguments);
    },

    _onHelp: function() {
        Ext.widget('helpwindow', {
            title: 'Help',
            width: 500,
            height: 400,
            helptext: '<p>Click on cells in the <em>Scale by</em> column to increase/decrease the weight of assignments.</p>' +
                '<h2>How it works</h2><p>Points are calculated as <code>scale-by * points / 100</code>.</p>' +
                '<h2>Warning</h2><p>Labels are <strong>not</strong> updated automatically when you change <em>Scale by</em>. You need to re-apply labels manually.</p>'
        }).show();
    }
});
