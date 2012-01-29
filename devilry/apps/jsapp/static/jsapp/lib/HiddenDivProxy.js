
Ext.define('jsapp.HiddenDivProxy', {
    extend: 'Ext.data.proxy.Proxy',
    alias: 'proxy.hiddendiv',

    /**
     * @cfg {Ext.data.Model[]} data
     * Optional array of Records to load into the Proxy
     */

    constructor: function(config) {
        this.callParent([config]);

        //ensures that the reader has been instantiated properly
        this.setReader(this.reader);
    },


    /**
     * Performs the given create operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    create: Ext.emptyFn,
    
    /**
     * Performs the given read operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    read: function(operation, callback, scope) {
        var me = this;
        var reader = me.getReader();
        var result = reader.read(me.data);
        Ext.apply(operation, {
            resultSet: result
        });
        operation.setCompleted();
        operation.setSuccessful();
        Ext.callback(callback, scope || me, [operation]);
    },
    
    /**
     * Performs the given update operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    update: Ext.emptyFn,
    
    /**
     * Performs the given destroy operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    destroy: Ext.emptyFn,
});

