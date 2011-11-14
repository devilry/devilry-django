Ext.define('devilry.administrator.ListOfChildnodes', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.administrator-listofchildnodes',
    cls: 'selectable-grid',
    hideHeaders: true,

    mixins: [
        'devilry.extjshelpers.AddPagerIfNeeded'
    ],

    /**
     * @cfg
     * Id of the parentnode.
     */
    parentnodeid: undefined,

    /**
     * @cfg
     * Orderby field.
     */
    orderby: undefined,

    /**
     * @cfg
     * Name of the model for the childnode type.
     */
    modelname: undefined,

    /**
     * @cfg
     * The part of the url that identifies this childnode type, such as "node" or "assignment".
     */
    urlrolepart: undefined,
    
    initComponent: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: this.modelname,
            remoteFilter: true,
            remoteSort: true
        });
        //this.store.pageSize = 2; // Uncomment to test paging
        this._loadStore();
        Ext.apply(this, {
            columns: [{
                header: 'Long name',  dataIndex: 'long_name', flex: 1
            }],
            listeners: {
                scope: this,
                select: this._onSelect
            }
        });
        this.callParent(arguments);
        this.addPagerIfNeeded();
    },

    _loadStore: function() {
        this.store.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.parentnodeid
        }]);
        this.store.proxy.setDevilryOrderby([this.orderby]);
        this.store.load();
    },

    _onSelect: function(grid, record) {
        var url = Ext.String.format('{0}/administrator/{1}/{2}', DevilrySettings.DEVILRY_URLPATH_PREFIX, this.urlrolepart, record.get('id'));
        window.location.href = url;
    }
});
