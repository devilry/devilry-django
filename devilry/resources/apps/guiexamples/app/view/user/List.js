Ext.define('guiexamples.view.user.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.userlist',

    title : 'All Users',

    store: 'Users',


    initComponent: function() {
        this.columns = [
            {header: 'Name',  dataIndex: 'username',  flex: 1},
            {header: 'Email', dataIndex: 'email', flex: 1}
        ];

        this.callParent(arguments);
    }
});
