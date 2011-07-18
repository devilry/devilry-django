/** A search result item (a single row in the search result).
 *
 * @xtype searchresultitem
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResultItem', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchresultitem',
    cls: 'searchresultitem',
    overCls: 'searchresultitem-hover',
    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` formatting template for the text content. _Required_.
         */
        tpl: undefined
    },
    layout: {
        type: 'hbox',
        align: 'top'
    },

    frame: false,

    initComponent: function() {

        var template = Ext.create('Ext.XTemplate', this.tpl);
        Ext.apply(this, {
            items: [{
                xtype: 'component',
                flex: 4,
                html: template.apply(this.record.data)
            }, {
                xtype: 'container',
                layout: {
                    type:'vbox',
                    padding:'5',
                    align:'stretch'
                },
                height: 70,
                width: 140,
                frame: false,
                //style: {"background-color": "red"},
                flex: 0,
                padding: {
                    left: 20 // Avoid text pressing against buttons
                },
                items: [{
                    xtype: 'button',
                    text: 'Default stuff'
                }, {
                    xtype: 'button',
                    text: 'More actions',
                    margin: {top: 5},
                    menu: [
                        {text: 'Item 1'},
                        {text: 'Item 2'},
                        {text: 'Item 3'},
                        {text: 'Item 4'}
                    ]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
