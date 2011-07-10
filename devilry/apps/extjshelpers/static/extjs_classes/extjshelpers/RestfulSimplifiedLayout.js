/** Layout for restful simplified editors.
 *
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administratorrestfulsimplifiedlayout',

    initComponent: function() {
        var me = this;

        var editformargs = {
            id: me.getChildIdBySuffix('editform'),
            xtype: 'form',
            layout: 'fit',
            disabled: true,
            model: this.model,
            items: this.editformitems
        };

        
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
            handler: function() {
                me.editform.getForm().submit({
                    submitEmptyText: true,
                    waitMsg: 'Saving item...',
                    success: function() {
                        me.readonly();
                    }
                });
            }
        };

        var editbuttonargs = {
            xtype: 'button',
            flex: 0,
            text: 'Edit',
            handler: function() {
                me.editable();
            }
        };


        Ext.apply(this, {
            items: [editformargs, {
                xtype: 'container',
                id: me.getChildIdBySuffix('buttoncarddeck'),
                layout: 'card',
                items: [{
                    xtype: 'container',
                    id: me.getChildIdBySuffix('readonlybuttons'),
                    height: 40,
                    layout: {
                        type: 'hbox',
                        pack: 'start',
                        align: 'stretch'
                    },
                    items: [
                        deletebuttonargs,
                        { xtype: 'tbspacer', flex: 1 }, 
                        editbuttonargs
                    ]
                }, {
                    xtype: 'container',
                    id: me.getChildIdBySuffix('editbuttons'),
                    height: 40,
                    layout: {
                        type: 'hbox',
                        pack: 'start',
                        align: 'stretch'
                    },
                    items: [{
                        xtype: 'tbspacer',
                        flex: 1
                    }, savebuttonargs ]
                }]
            }]
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

    readonly: function() {
        this.editform.disable();
        Ext.getCmp(this.getChildIdBySuffix('buttoncarddeck')).getLayout().setActiveItem(this.getChildIdBySuffix('readonlybuttons'));
    },
    editable: function() {
        this.editform.enable();
        Ext.getCmp(this.getChildIdBySuffix('buttoncarddeck')).getLayout().setActiveItem(this.getChildIdBySuffix('editbuttons'));
    },

    loadUpdateMode: function(record_id) {
        this.loadRecordFromStore(record_id);
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
