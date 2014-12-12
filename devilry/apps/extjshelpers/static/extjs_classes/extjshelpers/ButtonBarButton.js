/** A button in a {@link devilry.extjshelpers.ButtonBar}. */
Ext.define('devilry.extjshelpers.ButtonBarButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.buttonbarbutton',
    scale: 'large',
    hidden: true,

    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` for tooltip. (Optional).
         */
        tooltipTpl: Ext.create('Ext.XTemplate',
            '<div class="tooltip-title">{title}</div><p>{body}</p>'
        ),

        /**
         * @cfg
         * Tooltip config. Should be an Object with title and body attributes. (Required).
         */
        tooltipCfg: undefined,

        /**
         * @cfg
         * If defined, the handler is set to open this url.
         */
        clickurl: undefined,

        /**
         * @cfg
         * The store to use to check if this button should be visible. The store will have it pageSize set to 1.
         */
        store: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var me = this;
        this._loadStore();
        if(this.clickurl) {
            this.handler = function() {
                window.location = me.clickurl;
            }
        }
        Ext.apply(this, {
            listeners: {
                render: function() {
                    Ext.create('Ext.tip.ToolTip', {
                        target: me.id,
                        anchor: 'top',
                        dismissDelay: 30000,
                        html: me.tooltipTpl.apply(me.tooltipCfg)
                    });
                }
            },
        });
        this.callParent(arguments);
    },

    _loadStore: function() {
        this.store.load();
        this.store.on('load', function(store, records) {
            if(this.store.totalCount || this.is_superuser) {
                this.show();
            }
            hasRecords = (this.store.totalCount > 0 || this.is_superuser);
            this.up('buttonbar').notifyStoreLoad(hasRecords);
            //this.up('buttonbar').notifyStoreLoad(false);
        }, this);
    }
});
