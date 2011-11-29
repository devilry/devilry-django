Ext.define('devilry.i18n.TranslateGuiGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.translategui-grid',
    
    initComponent: function() {
        this.selModel = {
            selType: 'rowmodel',
            onCellSelect: function(position) {
                if (position.column != 1) {
                    position.column = 1;
                }
                return this.self.prototype.onCellSelect.call(this, position);
            }
        };

        var me = this;
        Ext.apply(this, {
            columnLines: true,
            selType: 'cellmodel',
            plugins: [
                Ext.create('Ext.grid.plugin.CellEditing', {
                    clicksToEdit: 1,
                    startEdit: function(record, column) {
                        var editcol = me.headerCt.gridDataColumns[2];
                        //console.log(me.headerCt.child('#translation'));
                        return this.self.prototype.startEdit.call(this, record, editcol);
                    }
                })
            ],
            columns: [{
                header: 'Key',
                flex: 1,
                minWidth: 250,
                dataIndex: 'key'
            }, {
                header: 'Default',
                flex: 5,
                dataIndex: 'defaultvalue'
            }, {
                header: 'Translation',
                flex: 5,
                dataIndex: 'translation',
                editor: 'textfield'
            }]
        });
        this.callParent(arguments);
    }
});
