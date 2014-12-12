Ext.define('devilry.statistics.ScalePointsPanel', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.statistics-scalepointspanel',
    requires: [
        'devilry.extjshelpers.HelpWindow',
        'devilry.extjshelpers.NotificationManager'
    ],

    saveMessageTpl: Ext.create('Ext.XTemplate',
        '{long_name}: {scale_points_percent}%'
    ),
    
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
                edit: this._onEdit
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

    _onEdit: function(editor, e) {
        Ext.getBody().mask('Saving point scale', 'page-load-mask');
        e.record.commit();
        e.record.save({
            scope: this,
            callback: this._onSaveComplete
        });
    },

    _onSaveComplete: function(record, op) {
        Ext.getBody().unmask();
        if(op.success) {
            this.loader.updateScaledPoints();
            devilry.extjshelpers.NotificationManager.show({
                title: 'Save successful',
                message: this.saveMessageTpl.apply(record.data)
            });
        } else {
            Ext.MessageBox.show({
                title: 'Failed to save point scale changes',
                msg: '<p>This is usually caused by an unstable server connection. Please try to reload the page.</p>',
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR,
                closable: false
            });
        }
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
