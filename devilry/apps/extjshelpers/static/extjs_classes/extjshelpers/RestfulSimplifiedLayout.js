/** 
 * @xtype administratorrestfulsimplifiedlayout
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedLayout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administratorrestfulsimplifiedlayout',

    initComponent: function() {
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
