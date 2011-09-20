/** 
 * REST proxy subclass which handles errors from {@link devilry.extjshelpers.RestSubmit}. 
 *
 * Since ExtJS for some reason goes into panic mode for any HTTP status
 * code except 200 (and ignores the response text), we need to override
 * setException in the REST proxy and manually decode the responseText.
 * ([see this forum thread](http://www.sencha.com/forum/showthread.php?135143-RESTful-Model-How-to-indicate-that-the-PUT-operation-failed&highlight=store+failure))
 *
 * However how do we get this into the form when we do not have any link to the form?
 *
 *  - We add the response and the the decoded responsedata to the operation
 *    object, which is available to onFailure in Submit.
 *
 * # Usage
 * 
 * First we need to use the proxy, for example in a ``Ext.data.Model``:
 *
 *     Ext.define('MyModel', {{
 *               extend: 'Ext.data.Model',
 *               requires: ['devilry.extjshelpers.RestProxy'],
 *               fields: [...],
                 proxy: Ext.create('devilry.extjshelpers.RestProxy', {
 *                   ...
 *               }
 *     });
 *
 * Then we can handle errors and access the error data as plain text or JSON.
 * See {@link #setException} for more details):
 *
 *     myform.getForm().doAction('devilryrestsubmit', {
 *         submitEmptyText: true,
 *         waitMsg: 'Saving item...',
 *         success: function(form, action) {...},
 *         failure: function(form, action) {
 *             var errorraw = action.operation.responseText;
 *             console.log(errorraw);
 *             var errorjson = action.operation.responseData;
 *             console.log(errorjson);
 *         }
 *     });
 *
 *
 * # See also
 * This should be used with {@link devilry.extjshelpers.RestSubmit}.
 * */
Ext.define('devilry.extjshelpers.RestProxy', {
    extend: 'Ext.data.proxy.Rest',
    alias: 'proxy.devilryrestproxy',

    constructor: function(config) {
        Ext.apply(this, {
            reader: {
                type: 'json',
                root: 'items',
                totalProperty: 'total'
            },
            writer: {
                type: 'json'
           }
        });

        this.callParent([config]);

        if(!this.extraParams) {
            this.extraParams = {};
        }
        this.extraParams.getdata_in_qrystring = true;
    },

    /**
     * Overrides error handling. Adds error information to the ``operation`` parameter.
     *
     * The error data is added to:
     *
     * - ``operation.responseText``: The data in the body of the HTTP response.
     * - ``operation.responseData``: If ``responseText`` can be decoded as JSON,
     *   this contains the decoded JSON object.
     */
    setException: function(operation, response){
        operation.response = response;
        operation.responseText = response.responseText;
        try {
            operation.responseData = Ext.JSON.decode(operation.responseText); // May want to use a Reader
        } catch(e) {
            // No operation.responseData if it can not be decoded as JSON.
        }
        operation.setException({
            status: response.status,
            statusText: response.statusText
        });
    },

    setDevilryResultFieldgroups: function(fieldgroups) {
        if(Ext.typeOf(fieldgroups) !== 'array') {
            throw "setDevilryResultFieldgroups(): fieldgroups must be an array";
        }
        this.extraParams.result_fieldgroups = Ext.JSON.encode(fieldgroups);
    },
    setDevilryFilters: function(filters) {
        if(Ext.typeOf(filters) !== 'array') {
            throw "setDevilryFilters(): filters must be an array";
        }
        this.extraParams.filters = Ext.JSON.encode(filters);
    },
    setDevilryOrderby: function(orderby) {
        if(Ext.typeOf(filters) !== 'array') {
            throw "setDevilryOrderby(): orderby must be an array";
        }
        this.extraParams.orderby = Ext.JSON.encode(orderby);
    },

    statics: {
        formatHtmlErrorMessage: function(operation) {
            var tpl = Ext.create('Ext.XTemplate', 
                '<div class="section errormessages">',
                '<tpl if="httperror">{httperror.status} {httperror.statusText}</tpl>',
                '<tpl for="errormessages">',
                '   <p>{.}</p>',
                '</tpl>',
                '</section>'
            );
            if(operation.responseData && operation.responseData.errormessages) {
                return tpl.apply({errormessages: operation.responseData.errormessages});
            } else {
                return tpl.apply({httperror: operation.error});
            }
        },

        showErrorMessagePopup: function(operation, title) {
            Ext.MessageBox.show({
                title: title,
                msg: devilry.extjshelpers.RestProxy.formatHtmlErrorMessage(operation),
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR
            });
        }
    }
});
