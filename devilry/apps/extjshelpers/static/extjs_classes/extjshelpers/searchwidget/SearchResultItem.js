/** A search result item (a single row in the search result).
 *
 * @xtype searchresultitem
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResultItem', {
    extend: 'Ext.container.Container',
    alias: 'widget.searchresultitem',
    cls: 'searchresultitem',
    frame: false,
    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` formatting template for the text content. _Required_.
         */
        tpl: '{id}'
    },
    layout: {
        type: 'hbox',
        align: 'top'
    },


    initComponent: function() {
        if(this.even) {
            this.addCls('searchresultitem-even');
        }

        var buttonitems = [];
        if(this.defaultbutton) {
            buttonitems.push(this.configureDefaultButton(this.defaultbutton));
        }
        if(this.menuitems) {
            buttonitems.push({
                xtype: 'button',
                text: 'More actions',
                margin: {top: 2},
                menu: this.menuitems
            });
        }

        var template = Ext.create('Ext.XTemplate', this.tpl);
        Ext.apply(this, {
            items: [{
                xtype: 'component',
                flex: 4,
                html: template.apply(this.recorddata)
            }, {
                xtype: 'container',
                flex: 0,

                frame: false,
                height: 65,
                width: 140,
                //style: {"background-color": "red"},
                padding: {
                    left: 20 // Avoid text pressing against buttons
                },
                layout: {
                    type:'vbox',
                    padding:'5',
                    align:'stretch'
                },
                items: buttonitems
            }]
        });
        this.callParent(arguments);
    },

    configureDefaultButton: function(config) {
        Ext.apply(config, {
            xtype: 'button'
        });
        if(config.clickLinkTpl) {
            var tpl = Ext.create('Ext.XTemplate', config.clickLinkTpl);
            var url = tpl.apply(this.recorddata);
            Ext.apply(config, {
                listeners: {
                    click: function() {
                        window.location = url;
                    }
                }
            });
        }
        return config;
    }
});
