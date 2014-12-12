/** Popup window used by {@link devilry.extjshelpers.formfields.ForeignKeySelector} */
Ext.define('devilry.extjshelpers.formfields.ForeignKeyBrowser', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.foreignkeybrowser',
    requires: [
        'devilry.extjshelpers.formfields.StoreSearchField'
    ],
    hideHeaders: true,
    border: false,

    /**
     * @cfg {string} [tpl]
     */
    tpl: '{id}',

    /**
     * @cfg {Ext.data.Model} [model]
     */
    model: undefined,

    /**
     * @cfg {Object} [foreignkeyselector]
     * The form field that the value ends up in.
     */
    foreignkeyselector: undefined,

    /**
     * @cfg {Boolean} [allowEmpty]
     * Allow empty field?
     */
    allowEmpty: false,


    initComponent: function() {
        var me = this;
        this.store = Ext.create('Ext.data.Store', {
            model: this.model,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true,
            autoLoad: true
        });

        var toolbarItems = [{
            xtype: 'storesearchfield',
            emptyText: 'Search...',
            store: this.store,
            autoLoadStore: false,
            listeners: {
                scope: this,
                render: function() {
                    var field = this.down('storesearchfield')
                    Ext.defer(function() {
                        field.focus();
                    }, 500, this);
                }
            }
        }];
        if(this.allowEmpty) {
            toolbarItems.push('->');
            toolbarItems.push({
                xtype: 'button',
                text: 'Clear value',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onClearValue
                }
            });
        }

        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: toolbarItems
            }, {
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: false
            }],

            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, record) {
                    return this.tpl.apply(record.data);
                }
            }],

            listeners: {
                scope: this,
                itemmouseup: this.onSelect
            }
        });
        this.callParent(arguments);

    },

    /**
     * @private
     */
    onClearValue: function() {
        this.foreignkeyselector.onClearValue();
        this.up('window').close();
    },

    /**
     * @private
     */
    onSelect: function(grid, record) {
        this.foreignkeyselector.onSelect(record);
        this.up('window').close();
    }
});
