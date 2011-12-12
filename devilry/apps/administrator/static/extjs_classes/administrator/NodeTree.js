Ext.define('devilry.administrator.NodeTree', {
    extend:'Ext.tree.Panel',
    alias:'widget.administrator-nodetree',

    initComponent:function () {
        this.store = Ext.create('Ext.data.TreeStore', {
            model:'devilry.corerest.administrator.Node',
            root:{
                long_name:'ROOT',
                short_name:'root',
                id:-1,
                expanded:true
            },
            nodeParam:'id' // The parameter we use to query for childnodes
        });
        Ext.apply(this, {
            hideHeaders:true,
            rootVisible:false,
            title:'Listing',
            collapsible:true,
            columns:[
                {
                    xtype:'treecolumn', //this is so we know which column will show the tree
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
            ]
        });
        this.callParent(arguments);
    }
});