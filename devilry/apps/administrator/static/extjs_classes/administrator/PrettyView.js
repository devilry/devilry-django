/** A prettyview is a read-only view panel used to display a single model record. */
Ext.define('devilry.administrator.PrettyView', {
    extend: 'Ext.panel.Panel',
    cls: 'prettyviewpanel',
    bodyPadding: 20,

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
         * The url to the dashboard. (Required). Used after delete to return to
         * the dashboard.
         */
        dashboardUrl: undefined

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
            'loadmodel',
            
            /**
             * @event
             * Fired when the edit button is clicked.
             * @param {Ext.model.Model} record The record to edit.
             * @param button The edit button.
             */
            'edit');
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.deletebutton = Ext.create('Ext.button.Button', {
            text: 'Delete',
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onDelete
            }
        });

        this.editbutton = Ext.create('Ext.button.Button', {
            text: 'Edit',
            enableToggle: true,
            menu: [],
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onEdit
            }
        });

        var tbar = ['->', this.deletebutton, this.editbutton];

        if(this.extraMeButtons) {
            Ext.Array.insert(tbar, 2, this.extraMeButtons);
        }

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

        this.addListener('render', function() {
            this.getEl().mask('Loading');
        }, this);
    },

    onModelLoadSuccess: function(record) {
        this.record = record;
        this.refreshBody();
        this.getEl().unmask();
        this.fireEvent('loadmodel', record);
    },

    refreshBody: function() {
        var bodyData = this.getExtraBodyData(this.record);
        Ext.apply(bodyData, this.record.data);
        this.update(this.bodyTpl.apply(bodyData));
    },

    getExtraBodyData: function(record) {
        return {};
    },

    onModelLoadFailure: function(record, operation) {
        throw 'Failed to load the model';
    },

    onEdit: function(button) {
        this.fireEvent('edit', this.record, button);
    },

    /** Set record. Triggers the loadmodel event. */
    setRecord: function(record) {
        this.onModelLoadSuccess(record);
    },

    onDelete: function() {
        var me = this;
        Ext.MessageBox.show({
            title: 'Confirm delete',
            msg: 'Are you sure you want to delete?',
            animateTarget: this.deletebutton,
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.ERROR,
            fn: function(btn) {
                if(btn == 'yes') {
                    me.deleteObject();
                }
            }
        });
    },

    deleteObject: function() {
        this.record.destroy();
        window.location.href = this.dashboardUrl;
    }
});
