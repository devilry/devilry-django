/** Apanel for editing RestfulSimplified models. */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.restfulsimplified_editpanel',
    requires: ['devilry.extjshelpers.RestSubmit'],

    config: {
        /**
         * @cfg
         * The name of the ``Ext.data.Model`` to present in the body. (Required).
         */
        modelname: undefined,

        /**
         * @cfg
         * Items for the ``Ext.form.Panel`` used to edit the RestfulSimplified object. (Required).
         */
        editformitems: undefined,

        /**
         * @cfg
         * List of foreign key field names in the model. (Required).
         */
        foreignkeyfieldnames: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.errorlist = Ext.create('devilry.extjshelpers.ErrorList');
        this.editform = Ext.ComponentManager.create({
            xtype: 'form',
            model: this.modelname,
            items: this.editformitems,

            // Fields will be arranged vertically, stretched to full width
            layout: 'anchor',
            defaults: {
                anchor: '100%',
            },

            cls: 'editform',
            bodyCls: 'editform-body',

            buttons: [{
                xtype: 'button',
                text: 'Save',
                scale: 'large',
                iconCls: 'icon-save-32',
                listeners: {
                    scope: this,
                    click: this.onSave
                }
            }]
        });

        Ext.apply(this, {
            items: [this.errorlist, this.editform]
        });
        this.callParent(arguments);

        if(this.record) {
            this.loadRecord();
        }
    },

    onSave: function() {
        this.errorlist.clearErrors();
        var me = this;
        this.editform.getForm().doAction('devilryrestsubmit', {
            submitEmptyText: true,
            waitMsg: 'Saving item...',
            success: function(form, action) {
                me.onSaveSuccess(form, action);
            },
            failure: function(form, action) {
                me.onSaveFailure(form, action);
            }
        });
    },

    onSaveSuccess: function(form, action) {
        var record = action.record;
        this.fireEvent('saveSucess', record);
    },

    onSaveFailure: function(form, action) {
        var errormessages = action.operation.responseData.items.errormessages;
        var me = this;
        Ext.each(errormessages, function(errormessage) {
            me.errorlist.addError(errormessage);
        });
    },

    loadRecord: function() {
        this.editform.loadRecord(this.record);

        // Set foreign key field values
        var fields = this.editform.getForm().getFields();
        var me = this;
        Ext.each(this.foreignkeyfieldnames, function(fieldname) {
            var field = fields.filter('name', fieldname).items[0];
            field.store.load(function(store, records, successful) {
                field.setValue(me.record.data[fieldname]);
            });
        });
    }
});
