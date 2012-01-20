Ext.define('devilry.administrator.ListOfChildnodes', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.administrator-listofchildnodes',
    cls: 'selectable-grid',
    hideHeaders: true,

    requires: [
        'devilry.extjshelpers.forms.administrator.Node',
        'devilry.extjshelpers.forms.administrator.Subject',
        'devilry.extjshelpers.forms.administrator.Period',
        'devilry.extjshelpers.forms.administrator.Assignment',
        'devilry.administrator.DefaultCreateWindow',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel'
    ],

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

    /**
     * @cfg
     * Readable type description.
     */
    readable_type: undefined,
    
    initComponent: function() {
        var model = Ext.ModelManager.getModel(this.modelname);
        this.store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
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
            },
            bbar: [{
                xtype: 'button',
                iconCls: 'icon-add-16',
                text: Ext.String.format('Add {0}', this.readable_type),
                listeners: {
                    scope: this,
                    click: this._onAdd
                }
            }]
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
    },

    _onAdd: function() {
        var successUrlPrefix = Ext.String.format('{0}/administrator/{1}/', DevilrySettings.DEVILRY_URLPATH_PREFIX, this.urlrolepart);
        Ext.create('devilry.administrator.DefaultCreateWindow', {
            title: Ext.String.format('Create new {0}', this.readable_type),
            editpanel: Ext.ComponentManager.create({
                xtype: 'restfulsimplified_editpanel',
                model: this.modelname,
                editform: Ext.widget(Ext.String.format('administrator_{0}form', this.urlrolepart)),
                record: Ext.create(this.modelname, {
                    parentnode: this.parentnodeid
                })
            }),
            successUrlTpl: Ext.create('Ext.XTemplate', successUrlPrefix + '{id}')
        }).show();
    }
});
