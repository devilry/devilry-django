/** 
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administratorrestfulsimplifiedlayout',

    deletebutton: {
        xtype: 'button',
        text: 'Delete',
        flex: 0,
        hidden: true,
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
    },

    savebutton: {
        xtype: 'button',
        text: 'Save',
        handler: function() {
            Ext.getCmp('editform').getForm().submit({
                submitEmptyText: true,
                waitMsg: 'Saving node...',
                success: function() {
                    this.editform.disable();
                    Ext.getCmp('editform-buttoncarddeck').getLayout().setActiveItem('editform-readonlybuttons');
                }
            });
        }
    },

    editbutton: {
        xtype: 'button',
        flex: 0,
        text: 'Edit',
        handler: function() {
            Ext.getCmp('editform').enable();
            Ext.getCmp('editform-buttoncarddeck').getLayout().setActiveItem('editform-editbuttons');
        }
    },

    initComponent: function() {
        if(this.supports_delete) {
            this.deletebutton.hidden = false;
        }

        var me = this;
        Ext.apply(this, {
            layout: 'card',
            items: [{
                xtype: 'panel',
                id: 'overview',
                html: '<h2>Overview</h2><p><strong>Search</strong>, <em>button</em> to create, .....</p>'
            }, {
                xtype: 'panel',
                id: 'editcard',
                items: [me.editform, {
                    xtype: 'container',
                    id: 'editform-buttoncarddeck',
                    layout: 'card',
                    items: [{
                        xtype: 'container',
                        id: 'editform-readonlybuttons',
                        height: 40,
                        layout: {
                            type: 'hbox',
                            pack: 'start',
                            align: 'stretch'
                        },
                        items: [
                            me.deletebutton,
                            { xtype: 'tbspacer', flex: 1 }, 
                            me.editbutton
                        ]
                    }, {
                        xtype: 'container',
                        id: 'editform-editbuttons',
                        height: 40,
                        layout: {
                            type: 'hbox',
                            pack: 'start',
                            align: 'stretch'
                        },
                        items: [{
                            xtype: 'tbspacer',
                            flex: 1
                        }, me.savebutton ]
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
