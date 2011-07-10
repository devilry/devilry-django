/** Layout for restful simplified editors.
 *
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.administratorrestfulsimplifiedlayout',
    border: 0,
    bodyStyle: {
        'background-color': 'transparent'
    },

    initComponent: function() {
        var me = this;
        
        var deletebuttonargs = {
            xtype: 'button',
            text: 'Delete',
            flex: 0,
            hidden: !this.supports_delete,
            handler: function() {
                // TODO: Confirm
                me.editform.submit({
                    submitEmptyText: true,
                    method: 'DELETE',
                    waitMsg: 'Deleting item...',
                    success: function() {
                    }
                });
            }
        };

        var savebuttonargs = {
            xtype: 'button',
            text: 'Save',
            scale: 'large',
            handler: function() {
                me.editform.getForm().submit({
                    submitEmptyText: true,
                    waitMsg: 'Saving item...',
                    success: function(form, action) {
                        var record = action.record;
                        me.editform.loadRecord(record); // Need to load the record. If not, the proxy will do a POST instead of PUT on next save.
                        me.readonly();
                    }
                });
            }
        };

        var clicktoeditbuttonargs = {
            xtype: 'button',
            //scale: 'large',
            text: 'Click to edit',
            listeners: {
                click: function(button, pressed) {
                    me.editable();
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

            bodyStyle: {
                padding: '15px'
            },

            // Disable by default
            disabled: true,

            // Only save button. Other buttons are in overlayBar
            buttons: [
                savebuttonargs,
            ]
        };


        Ext.apply(this, {
            items: [editformargs],
            layout: 'fit'
        });
        this.callParent(arguments);

        this.editform = Ext.getCmp(editformargs.id);
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
                //var title = Ext.String.format('Edit', record.data.long_name, record.data.short_name);
                //me.editform.setTitle(title);
                var fields = me.editform.getForm().getFields();
                Ext.each(me.foreignkeys, function(fieldname) {
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
        this.overlayBar.alignTo(this, 'tr-tr');
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
