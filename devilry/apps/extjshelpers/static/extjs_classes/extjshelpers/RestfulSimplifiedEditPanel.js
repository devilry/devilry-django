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
         * List of foreign key field names in the model. (Required).
         */
        foreignkeyfieldnames: undefined,

        /**
         * @cfg
         * A instance of the ``Ext.data.Model`` which should be loaded into the
         * form.
         */
        record: undefined
    },
    cls: 'editform',
    bodyCls: 'editform-body',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.errorlist = Ext.create('devilry.extjshelpers.ErrorList');
        this.model = Ext.ModelManager.getModel(this.model);

        this.editform.frame = false;
        if(this.editform.flex == undefined) {
            this.editform.flex = 15;
        }
        this.editform.border = 0;

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },

            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [this.editform, {
                xtype: 'panel',
                frame: false,
                border: false,
                bodyCls: 'editform-sidebar',
                flex: 5,
                items: [this.errorlist, {
                    xtype: 'box',
                    html: this.parseHelp()
                }]
            }]
        });
        this.dockedItems = [{
            xtype: 'toolbar',
            dock: 'bottom',
            ui: 'footer',
            defaults: {minWidth: 75},

            items: ['->', {
                xtype: 'button',
                text: 'Save',
                scale: 'large',
                iconCls: 'icon-save-32',
                listeners: {
                    scope: this,
                    click: this.onSave
                }
            }]
        }];
        this.callParent(arguments);

        if(this.record) {
            this.loadRecord();
        }
    },

    parseHelp: function() {
        if(!this.editform.help) {
            return '';
        }
        var help = '';
        var me = this;
        var state = this.record == undefined? 'new': 'existing';
        Ext.Array.each(this.editform.help, function(helpobj) {
            if(Ext.typeOf(helpobj) === 'string') {
                helpobj = {text: helpobj};
            }
            if(helpobj.state == undefined || (helpobj.state == state)) {
                help += Ext.String.format('<p>{0}</p>', helpobj.text);
            }
        });
        return help;
    },

    onSave: function() {
        this.errorlist.clearErrors();
        var me = this;

        this.editform.getForm().doAction('devilryrestsubmit', {
            submitEmptyText: true,
            waitMsg: 'Saving item...',
            model: this.model,
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

    onSaveFailure: function(record, action) {
        var errormessages = action.operation.responseData.items.errormessages;
        var me = this;
        Ext.each(errormessages, function(errormessage) {
            me.errorlist.addError(errormessage);
        });
    },

    loadRecord: function() {
        this.editform.loadRecord(this.record);
    }
});
