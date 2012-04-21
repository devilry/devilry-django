/**
 * Provides a convenient method of finding a record:
 *
 * 1. Check from an internal cache.
 * 2. Check from from a list of stores.
 * 3. Get using the model proxy.
 * */
Ext.define('themebase.RecordCache', {
    config: {
        /**
        * @cfg
        * Array of ``Ext.data.Store``.
        */
        stores: [],

        /**
        * @cfg
        * An ``Ext.data.Model``. Required.
        */
        model: undefined,

        idProperty: 'id'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.cache = {};
        //console.log(this.model.prototype);
        //Ext.Array.each(this.stores, function(store) {
            //store.on('load', this._onStoreLoad, this);
        //}, this);
    },

    //_onStoreLoad: function(store, records) {
        //this._addMany(records);
    //},

    //_addMany: function(records) {
        //Ext.Array.each(records, function(record) {
            //this.
        //}, this);
    //},
    
    /** Find in the cache of the stores.
     * @return The record if it is found, otherwise return ``null``.
     * */
    _findByInStores: function(fn, scope) {
        var i;
        for(i=0; i<this.stores.length; i++) {
            var store = this.stores[i];
            var recordIndex = store.findBy(fn, scope);
            if(recordIndex != -1) {
                return store.getAt(recordIndex);
            }
        }
        return null;
    },

    /** Find in the cache.
     * @return The record if it is found, otherwise return ``null``.
     * */
    _findByInCache: function(fn, scope) {
        var foundRecord = null;
        Ext.Object.each(this.cache, function(id, record) {
            var match = Ext.bind(fn, scope)(record);
            if(match) {
                foundRecord = record;
                return; // Bread
            }
        }, this);
        return foundRecord;
    },

    findBy: function(fn, scope) {
        var record;
        record = this._findByInCache(fn, scope);
        if(record != null) {
            return record;
        }
        record = this._findByInStores(fn, scope);
        if(record != null) {
            return record;
        }
        return null;
    },

    put: function(record) {
        var id = record.get(this.idProperty);
        this.cache[id] = record;
    },
});
