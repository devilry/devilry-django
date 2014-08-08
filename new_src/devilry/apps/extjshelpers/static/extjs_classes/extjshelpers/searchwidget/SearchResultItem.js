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

        var template = Ext.create('Ext.XTemplate', this.tpl);
        var items = [{
            xtype: 'component',
            flex: 4,
            html: template.apply(this.recorddata)
        }];

        var button = this.defaultbutton;
        if(this.defaultbutton) {
            if(this.menuitems) {
                this.configureClickable(button, 'splitbutton');
                button.menu = {
                    items: this.configureMenuItems()
                }
            } else {
                this.configureClickable(button, 'button');
            }

            Ext.apply(button, {
                minWidth: 100,
                margin: '0 0 0 10 0'
            });
            items.push(button);
        }

        Ext.apply(this, {items: items});
        this.callParent(arguments);
    },


    configureMenuItems: function() {
        var me = this;
        Ext.each(this.menuitems, function(menuitem) {
            me.configureClickable(menuitem);
        });
        return this.menuitems;
    },

    configureClickable: function(config, xtype) {
        Ext.apply(config, {
            xtype: xtype,
            scale: 'medium'
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
