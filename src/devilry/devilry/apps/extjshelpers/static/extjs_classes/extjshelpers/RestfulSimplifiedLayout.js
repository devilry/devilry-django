/** Layout for restful simplified editors.
 *
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.administratorrestfulsimplifiedlayout',
    requires: [
        'devilry.extjshelpers.ErrorList',
        'devilry.extjshelpers.RestSubmit'
    ],
    border: 0,

    config: {
        /**
         * @cfg
         * Items for the ``Ext.form.Panel`` used to edit the RestfulSimplified object. (Required).
         */
        editformitems: undefined,

        /**
         * @cfg
         * ``Ext.data.Model`` for the RestfulSimplified object. (Required).
         */
        model: undefined,

        /**
         * @cfg
         * Does the RestfulSimplified support delete? (Required).
         */
        supports_delete: undefined,

        /**
         * @cfg
         * List of foreign key field names in the model. (Required).
         */
        foreignkeyfieldnames: undefined
    },

    bodyStyle: {
        'background-color': 'transparent'
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;
        
        var savebuttonargs = {
            xtype: 'button',
            text: 'Save',
            scale: 'large',
            iconCls: 'icon-save-32',
            handler: function() {
                me.errorlist.clearErrors();
                me.editform.getForm().doAction('devilryrestsubmit', {
                    submitEmptyText: true,
                    waitMsg: 'Saving item...',
                    success: function(form, action) {
                        var record = action.record;
                        me.editform.loadRecord(record); // Need to load the record. If not, the proxy will do a POST instead of PUT on next save.
                        me.readonly();
                    },
                    failure: function(form, action) {
                        var errormessages = action.operation.responseData.items.errormessages;
                        Ext.each(errormessages, function(errormessage) {
                            me.errorlist.addError(errormessage);
                        });
                    }
                });
            }
        };

        var deletebuttonargs = {
            xtype: 'button',
            text: 'Delete',
            flex: 0,
            hidden: !this.supports_delete,
            scale: 'large',
            iconCls: 'icon-delete-32',
            handler: function() {
                Ext.MessageBox.show({
                    title: 'Confirm delete',
                    msg: 'Are you sure you want to delete?',
                    animateTarget: this,
                    buttons: Ext.Msg.YESNO,
                    icon: Ext.Msg.ERROR,
                    fn: function(btn) {
                        if(btn == 'yes') {
                            me.deleteCurrent();
                        }
                    }
                });
            }
        };

        var clicktoeditbuttonargs = {
            xtype: 'button',
            text: 'Click to edit',
            scale: 'large',
            iconCls: 'icon-edit-32',
            listeners: {
                click: function(button, pressed) {
                    me.editable();
                    //me.errorlist.addError('Hello world');
                    //me.errorlist.addError('This is a long error message. Message message message message message message message message message message message message message message message message message message message message message message message message message message message message.');
                }
            }
        };

        this.overlayBar = Ext.create('Ext.container.Container', {
            floating: true,
            cls: 'form-overlay-bar',
            height: 40,
            width: 300,
            layout: {
                type: 'hbox',
                align: 'stretch',
                pack: 'end'
            },
            items: [
                deletebuttonargs,
                {xtype: 'component', width: 10},
                clicktoeditbuttonargs
            ]
        });


        this.errorlist = Ext.create('devilry.extjshelpers.ErrorList', {});

        var editformargs = {
            id: me.getChildIdBySuffix('editform'),
            xtype: 'form',
            model: this.model,
            items: this.editformitems,

            // Fields will be arranged vertically, stretched to full width
            layout: 'anchor',
            defaults: {
                anchor: '100%',
            },

            cls: 'editform',
            bodyCls: 'editform-body',

            // Disable by default
            disabled: true,

            // Only save button. Other buttons are in overlayBar
            buttons: [
                savebuttonargs
            ]
        };


        Ext.apply(this, {
            items: [
                this.errorlist,
                editformargs
            ],
            layout: 'fit'
        });
        this.callParent(arguments);

        this.editform = Ext.getCmp(editformargs.id);
    },

    deleteCurrent: function() {
        this.editform.getForm().doAction('devilryrestsubmit', {
            submitEmptyText: true,
            method: 'DELETE',
            waitMsg: 'Deleting item...',
            success: function() {
            }
        });
    },

    getChildIdBySuffix: function(idsuffix) {
        return this.id + '-' + idsuffix;
    },


    /** Load the request record into the form. */
    loadRecordFromStore: function (record_id) {
        var me = this;
        Ext.ModelManager.getModel(this.model).load(record_id, {
            success: function(record) {
                me.editform.loadRecord(record);
                var fields = me.editform.getForm().getFields();
                Ext.each(me.foreignkeyfieldnames, function(fieldname) {
                    var field = fields.filter('name', fieldname).items[0];
                    field.store.load(function(store, records, successful) {
                        field.setValue(record.data[fieldname]);
                    });
                });
            }
        });
    },

    getFormButtonBar: function() {
        return this.editform.dockedItems.items[0];
    },

    readonly: function() {
        this.editform.disable();
        this.overlayBar.show();
        this.overlayBar.alignTo(this.editform, 'tr-tr');
        this.getFormButtonBar().hide();
    },
    editable: function() {
        this.editform.enable();
        this.overlayBar.hide();
        this.getFormButtonBar().show();
    },

    loadUpdateMode: function(record_id) {
        this.loadRecordFromStore(record_id);
        this.readonly();
    },
    loadCreateMode: function() {
        this.getFormButtonBar().hide(); // NOTE: This is required for some reason?
        this.editable();
    },
    loadMode: function(mode, record_id) {
        if(mode == "update") {
            this.loadUpdateMode(record_id);
        } else if(mode == "create") {
            this.loadCreateMode();
        }
    }
});
