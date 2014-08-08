/** Store with defaults tuned for Devilry and some extra utility functions. */
Ext.define('devilry.extjshelpers.Store', {
    extend: 'Ext.data.Store',

    config: {
        remoteFilter: true,
        remoteSort: true,
        autoSync: true
    },

    constructor: function(config) {
        this.callParent([config]);

        this.addEvents(
            /**
             * @event
             * Fired when loadAll() has successfully loaded all records. Same params as the load event.
             */
            'loadAll'
        );
    },

    /**
     * Load all records in the store. This is done in two requests. First we
     * ask for a single record, to get the totalCount, then we ask for all
     * records.
     *
     * @param options Same as for ``Ext.data.Store.load``.
     */
    loadAll: function(options) {
        this.pageSize = 1;
        var me = this;
        this.load({
            callback: function(records, operation, success) {
                if(success) {
                    me.pageSize = me.totalCount;
                    me.load(function(records, operation, success) {
                        me._callbackFromOptions(options, [records, operation, success]);
                        me.fireEvent('loadAll', me, records, success, operation);
                    });
                } else {
                    me._callbackFromOptions(options, [records, operation, false]);
                }
            }
        });
    },

    _callbackFromOptions: function(options, args) {
        if(Ext.typeOf(options) == 'function') {
            Ext.bind(options, this, args)();
        } else if(Ext.typeOf(options) == 'object' && options.callback) {
            Ext.bind(options.callback, options.scope, args)();
        }
    }
});
