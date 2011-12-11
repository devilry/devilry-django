Ext.define('devilry.administrator.NodeBrowser', {
    extend:'Ext.grid.Panel',
    requires:[
        'devilry.corerest.administrator.Node'
    ],

    initComponent:function () {
        this.store = Ext.create('Ext.data.Store', {
            model:'devilry.corerest.administrator.Node',
            autoSync: true
        });
        Ext.apply(this, {
            selType: 'cellmodel',
            plugins: [
                Ext.create('Ext.grid.plugin.CellEditing', {
                    clicksToEdit: 1
                })
            ],
            columns:[
                {
                    header: 'ID',
                    dataIndex: 'id',
                    width: 50
                },
                {
                    header:'Short name',
                    dataIndex:'short_name',
                    field:'textfield',
                    flex:1
                },
                {
                    header:'Long name',
                    dataIndex:'long_name',
                    field: 'textfield',
                    flex:2
                }
            ]
        });
        this.callParent(arguments);
        this.store.load({
            callback: function(records) {
                console.log(records);
            }
        });
    }
});
