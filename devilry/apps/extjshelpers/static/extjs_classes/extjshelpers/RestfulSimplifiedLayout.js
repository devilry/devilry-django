/** 
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administratorrestfulsimplifiedlayout',

    initComponent: function() {
        var me = this;

        var editformargs = {
            id: 'stuff',
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
                Ext.getCmp('editform').submit({
                    submitEmptyText: true,
                    method: 'DELETE',
                    waitMsg: 'Deleting node...',
                    success: function() {
                    }
                });
            }
        };

        var savebuttonargs = {
            xtype: 'button',
            text: 'Save',
            handler: function() {
                Ext.getCmp('editform').getForm().submit({
                    submitEmptyText: true,
                    waitMsg: 'Saving node...',
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
            success: function(node) {
                me.editform.loadRecord(node);
                var title = Ext.String.format('{0} ({1})', node.data.long_name, node.data.short_name);
                me.editform.setTitle(title);
            }
        });
    },

    loadUpdateMode: function(record_id) {
        var c = Ext.getCmp(this.getChildIdBySuffix('edit-card'));
        this.getLayout().setActiveItem(c);
        this.loadRecordFromStore(record_id);
    },


    loadMode: function(mode, record_id) {
        if(mode == "update")
            this.loadUpdateMode(record_id);
        else if(mode == "overview")
            this.loadOverviewMode();
    }
});
