/** A data proxy suitable for testing.
 *
 * It adds a hidden extjs window to the body. This window contains the proxy
 * data. Testing frameworks like selenium can then easily be used to assert the
 * content of this window.
 *
 * For apps using ``jsapp.Router`` (or other non-reloading methods of changing
 * view) this has an additional advantage. The window persists when
 * the route changes. This makes it possible to test that transitions from one
 * view to the next works, such as "Create new" that redirects to a view of the
 * resulting item.
 * */
Ext.define('jsapp.HiddenElementProxy', {
    extend: 'Ext.data.proxy.Proxy',
    alias: 'proxy.hiddenelement',
    requires: [
        'Ext.window.Window',
        'Ext.util.MixedCollection',
        'Ext.form.field.TextArea'
    ],

    /**
     * @cfg {Ext.data.Model[]} data
     * Optional array of Records to load into the Proxy
     */

    /**
     * @cfg {String} id
     * A required ID for the element that will be created to contain the data.
     * The actual data will be contained within a div with "<id>-body" as ID.
     */
    id: undefined,

    /**
     * @cfg
     * Show the container window at the top right corner of the screen?
     */
    show: false,

    /**
     * @cfg validator
     * An optional validator that may be used to change the operation.
     */

    constructor: function(config) {
        this.callParent([config]);
        this.data = new Ext.util.MixedCollection();
        this.container = Ext.widget('window', {
            width: 400,
            height: 500,
            layout: 'fit',
            plain: true,
            border: false,
            shadow: true,
            maximizable: true,
            items: [{
                xtype: 'panel',
                bodyStyle: 'white-space:pre',
                autoScroll: true,
                id: this.id
            }]
        });

        // Make sure the component is added to the document at once
        this.container.show();
        this.container.hide();

        // We defer show() and alignTo to give the UI time to draw itself
        // first.
        if(this.show) {
            Ext.defer(function() {
                this._show();
            }, 1000, this);
        }
        //this.setReader(this.reader);
    },

    _show: function() {
        this.container.show();
        this.container.alignTo(document, 'tl-tr', [-10 - this.container.width, 10]);
    },

    _formatDataAsJSON: function() {
        var out = [];
        this.data.each(function(item) {
            var itemout = [];
            Ext.Object.each(item, function(key, value) {
                itemout.push(Ext.String.format('{0}: {1}',
                    Ext.JSON.encode(key), Ext.JSON.encode(value)
                ));
            });
            var itemjson = '{' + itemout.join(',\n   ') + '}';
            out.push(itemjson);
        }, this);
        var outdata = Ext.String.format('[\n  {0}\n]', out.join(',\n\n  '));
        Ext.JSON.decode(outdata); // This fails if the data formatting above does not produce valid JSON
        return outdata;
    },

    _updateContainer: function() {
        var outdata = this._formatDataAsJSON();
        Ext.getCmp(this.id).update(outdata);
    },

    /**
     * Performs the given create operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    create: function(operation, callback, scope) {
        operation.setStarted();
        var records = operation.getRecords();

        Ext.callback(this.validator, this, ['create', operation]);

        if(!operation.hasException()) {
            Ext.Array.each(records, function(record) {
                this.data.add(record.id, record.data);
            }, this);
            this._updateContainer();
            operation.setSuccessful();
        }
        operation.setCompleted();
        Ext.callback(callback, scope || this, [operation]);
    },
    
    /**
     * Performs the given read operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    read: function(operation, callback, scope) {
        console.warn('read is not supported ye');
        //var me = this;
        //var reader = me.getReader();
        //var result = reader.read(me.data);
        //Ext.apply(operation, {
            //resultSet: result
        //});
        //operation.setCompleted();
        //operation.setSuccessful();
        //Ext.callback(callback, scope || me, [operation]);
    },
    
    /**
     * Performs the given update operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    update: function() {
        console.warn('update is not supported ye');
    },
    
    /**
     * Performs the given destroy operation.
     * @param {Ext.data.Operation} operation The Operation to perform
     * @param {Function} callback Callback function to be called when the Operation has completed (whether successful or not)
     * @param {Object} scope Scope to execute the callback function in
     * @method
     */
    destroy: function() {
        console.warn('destroy is not supported ye');
    }
});
