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
        tpl: undefined,

        recorddata: undefined,
        recordindex: undefined,
        defaultbutton: undefined,
        menuitems: undefined
    },
    layout: {
        type: 'hbox',
        align: 'top'
    },


    initComponent: function() {
        if(this.recordindex % 2 != 0) {
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
            this.applyClickLinkButton(config);
        } else if(config.clickFilter) {
            this.applyClickFilterButton(config);
        }
        return config;
    },

    applyClickLinkButton: function(config) {
        var tpl = Ext.create('Ext.XTemplate', config.clickLinkTpl);
        var url = tpl.apply(this.recorddata);
        Ext.apply(config, {
            listeners: {
                click: function() {
                    window.location = url;
                }
            }
        });
    },

    applyClickFilterButton: function(config) {
        var tpl = Ext.create('Ext.XTemplate', config.clickFilter);
        var filter = tpl.apply(this.recorddata);
        var me = this;
        Ext.apply(config, {
            listeners: {
                click: function() {
                    var searchwidget = me.getSearchWidget();
                    searchwidget.setSearchValue(filter);
                }
            }
        });
    },

    getSearchWidget: function() {
        return this.up('multisearchresults').getSearchWidget();
    }
});
