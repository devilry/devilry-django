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
                        me.editform.disable();
                        Ext.getCmp(me.getChildIdBySuffix('buttoncarddeck')).getLayout().setActiveItem(me.getChildIdBySuffix('readonlybuttons'));
                    }
                });
            }
        };

        var editbuttonargs = {
            xtype: 'button',
            flex: 0,
            text: 'Edit',
            handler: function() {
                me.editform.enable();
                Ext.getCmp(me.getChildIdBySuffix('buttoncarddeck')).getLayout().setActiveItem(me.getChildIdBySuffix('editbuttons'));
            }
        };



        Ext.apply(this, {
            layout: 'card',
            items: [{
                xtype: 'panel',
                id: me.getChildIdBySuffix('overview-card'),
                html: '<h2>Overview</h2><p><strong>Search</strong>, <em>button</em> to create, .....</p>'
            }, {
                xtype: 'panel',
                id: me.getChildIdBySuffix('edit-card'),
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
            }]
        });
        this.callParent(arguments);

        this.editform = Ext.getCmp(editformargs.id);
    },

    loadOverviewMode: function() {
        this.getLayout().setActiveItem(this.getChildIdBySuffix('overview-card'));
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
                var title = Ext.String.format('{0} ({1})', record.data.long_name, record.data.short_name);
                me.editform.setTitle(title);
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

    loadUpdateMode: function(record_id) {
        var editcard = Ext.getCmp(this.getChildIdBySuffix('edit-card'));
        this.getLayout().setActiveItem(editcard);
        this.loadRecordFromStore(record_id);
    },

    loadCreateMode: function() {
        var editcard = Ext.getCmp(this.getChildIdBySuffix('edit-card'));
        this.getLayout().setActiveItem(editcard);
        this.editform.enable();
    },


    loadMode: function(mode, record_id) {
        if(mode == "update") {
            this.loadUpdateMode(record_id);
        } else if(mode == "overview") {
            this.loadOverviewMode();
        } else if(mode == "create") {
            this.loadCreateMode();
        }
    }
});
