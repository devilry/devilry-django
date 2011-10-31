Ext.define('devilry.administrator.SimplifiedBulkActions', {
    requires: [
        'devilry.extjshelpers.RestProxy'
    ],

    config: {
        /**
         * @cfg
         * The URL path of the API without the prefix of the Devilry instance.
         * Example: "/administrator/restfulsimplifiedassignmentgroup/"
         */
        apipath: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.url = Ext.String.format('{0}{1}', DevilrySettings.DEVILRY_URLPATH_PREFIX, this.apipath);
    },


    /**
     * @private
     * Sanity check to make this easier to debug.
     * Throws an exception of the check fails, and this exception should not be
     * handled, since it is always a bug if it is thrown.
     */
    _sanityCheckData: function(data) {
        if(!Ext.typeOf(data) != 'array') {
            throw "Data must be an array";
        }
    },

    _sendRestRequest: function(data) {
        this._sanityCheckData(data);
        Ext.apply(data, {
            url: this.url
        });
        Ext.Ajax.request(args);

    },

    createMany: function(options) {
        this._sendRestRequest({
            params: Ext.JSON.encode(options.data),
            method: 'POST',
            scope: options.scope,
            callback: options.callback
        });
    },

    updateMany: function(options) {
        this._sendRestRequest({
            params: Ext.JSON.encode(options.data),
            method: 'PUT',
            scope: options.scope,
            callback: options.callback
        });
    },

    deleteMany: function(options) {
        this._sendRestRequest({
            params: Ext.JSON.encode(options.data),
            method: 'DELETE',
            scope: options.scope,
            callback: options.callback
        });
    }
});
