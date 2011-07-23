/** A prettyview is a read-only view panel used to display a single model record. */
Ext.define('devilry.administrator.PrettyView', {
    extend: 'Ext.panel.Panel',
    cls: 'prettyviewpanel',

    config: {
        /**
         * @cfg
         * The name of the ``Ext.data.Model`` to present in the body. (Required).
         */
        modelname: undefined,

        /**
         * @cfg
         * Unique ID of the object to load from the model. (Required).
         */
        objectid: undefined,

        /**
         * @cfg
         * A ``Ext.XTemplate`` object for the body of this view. (Required).
         */
        bodyTpl: undefined,

        /**
         * @cfg
         * Optional list of buttons for related actions.
         */
        relatedButtons: undefined,

        /**
         * @cfg
         * Optional list of menuitems for plugin actions.
         */
        //pluginItems: undefined
    },

    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when the model record is loaded successfully.
             * @param {Ext.model.Model} record The loaded record.
             */
            'loadmodel');
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var tbar = ['->', {
            xtype: 'button',
            text: 'Delete',
            scale: 'medium',
            listeners: {
                scope: this,
                click: this.onDelete
            }
        }, {
            xtype: 'button',
            text: 'Edit',
            scale: 'medium',
            listeners: {
                scope: this,
                click: this.onEdit
            }
        }];

        //if(this.pluginItems) {
            //Ext.Array.insert(tbar, 0, this.pluginItems);
        //}

        if(this.relatedButtons) {
            Ext.Array.insert(tbar, 0, this.relatedButtons);
        }

        Ext.apply(this, {
            tbar: tbar,
        });
        this.callParent(arguments);

        var model = Ext.ModelManager.getModel(this.modelname);
        model.load(this.objectid, {
            scope: this,
            success: this.onModelLoadSuccess,
            failure: this.onModelLoadFailure
        });
    },

    onModelLoadSuccess: function(record, operation) {
        this.fireEvent('loadmodel', record);
        this.update(this.bodyTpl.apply(record.data));
    },

    onModelLoadFailure: function(record, operation) {
        throw 'Failed to load the model';
    },

    onEdit: function() {
        console.log('edit');
    },

    onDelete: function() {
        console.log('delete');
    }
});
