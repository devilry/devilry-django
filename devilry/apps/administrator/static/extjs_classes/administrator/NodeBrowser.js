Ext.define('devilry.administrator.NodeBrowser', {
    extend:'Ext.grid.Panel',
    requires:[
        'devilry.corerest.administrator.Node'
    ],

    initComponent:function () {
        this.store = Ext.create('Ext.data.Store', {
            model:'devilry.corerest.administrator.Node',
            autoSync:true
        });
        Ext.apply(this, {
//            selType: 'cellmodel',
//            plugins: [
//                Ext.create('Ext.grid.plugin.CellEditing', {
//                    clicksToEdit: 1
//                })
//            ],
//            tbar:[
//                {
//                    xtype:'button',
//                    iconCls:'icon-up-32',
//                    scale:'large',
//                    listeners:{
//                        scope:this,
//                        click:this._onUp
//                    }
//                }
//            ],
            columns:[
                {
                    header:'ID',
                    dataIndex:'id',
                    width:50
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
                    field:'textfield',
                    flex:2
                }
            ],

            listeners:{
                scope:this,
                select:this._onSelect
            }
        });
        this.callParent(arguments);
        this.current = undefined;
        this._load();
    },

    _load:function (id) {
        var params = {};
        if(id !== undefined) {
            params.id = id;
        }
        this.store.load({
            scope: this,
            params: params,
            callback: function(records, op, success) {
                console.log("success", success);
            }
        });
    },

    _onSelect:function (rowmodel, record) {
        this._load(record.get('id'));
    }
//
//    _onUp:function () {
//        this._load(this.current.get('parentnode_id'));
//    }

});
