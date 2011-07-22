/** Pager which can be used with any store. */
Ext.define('devilry.extjshelpers.Pager', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilrypager',
    cls: 'widget-devilrypager',

    layout: {
        type: 'hbox',
        align: 'middle'
    },

    config: {
        /**
         * @cfg
         * An ``Ext.data.Store``.
         */
        store: undefined,

        /**
         * @cfg
         * The ``Ext.XTemplate for the label between the next and previous buttons.
         */
        middleLabelTpl: Ext.create('Ext.XTemplate', '{from}-{to} of {total}'),

        /**
         * @cfg
         * Width of the entire container. Note that the label is stretched
         * while the buttons keep their width.
         */
        width: 150,

        /**
         * @cfg
         * Width of the container.
         */
        height: 30,

        /**
         * @cfg
         * Reverse direction? If this is ``true``, the next button goes backwards, and the previous button goes forward.
         */
        reverseDirection: false
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            items: [{
                xtype: 'button',
                text: '<',
                flex: 0,
                id: this.id + (this.reverseDirection? '-next': '-prev'),
                disabled: true,
                listeners: {
                    click: function() {
                        me.reverseDirection? me.store.nextPage(): me.store.previousPage();
                    }
                },
            }, {
                xtype: 'component',
                html: '',
                style: {
                    'text-align': 'center'
                },
                flex: 1,
                width: 200,
                id: this.id + '-label',
            }, {
                xtype: 'button',
                text: '>',
                flex: 0,
                id: this.id + (this.reverseDirection? '-prev': '-next'),
                disabled: true,
                listeners: {
                    click: function() {
                        me.reverseDirection? me.store.previousPage(): me.store.nextPage();
                    }
                }
            }]
        });

        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.updatePageSwitcher(records);
            }
        });

        this.callParent(arguments);
    },

    updatePageSwitcher: function(records) {
        var from = this.store.pageSize * (this.store.currentPage-1);
        var visibleOnCurrentPage = this.store.getCount();
        var totalPages = this.store.getTotalCount() / this.store.pageSize;

        var label = this.middleLabelTpl.apply({
            total: this.store.getTotalCount(),
            from: from,
            to: from + visibleOnCurrentPage,
            //records: records, // Enable if we need it anywhere
            firstRecord: records.length == 0? undefined: records[0],
            currentPage: this.store.currentPage,
            currentNegativePageOffset: totalPages - this.store.currentPage + 1
        });
        this.getMiddleLabel().update(label);

        this.getPreviousPageButton().disable();
        if(from > 0) {
            this.getPreviousPageButton().enable();
        }
        this.getNextPageButton().disable();
        if(visibleOnCurrentPage == this.store.pageSize && (from+visibleOnCurrentPage) != this.store.getTotalCount()) {
            this.getNextPageButton().enable();
        }
    },
    getMiddleLabel: function() {
        return Ext.getCmp(this.id + '-label');
    },
    getPreviousPageButton: function() {
        return Ext.getCmp(this.id + '-prev');
    },
    getNextPageButton: function() {
        return Ext.getCmp(this.id + '-next');
    }
});
