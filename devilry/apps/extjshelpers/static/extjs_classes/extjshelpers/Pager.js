/** Pager which can be used with any store. */
Ext.define('devilry.extjshelpers.Pager', {
    extend: 'Ext.toolbar.Toolbar',
    alias: 'widget.devilrypager',
    cls: 'widget-devilrypager',
    style: {
        border: 'none'
    },

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
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var me = this;

        this.previousButton = Ext.ComponentManager.create({
            xtype: 'button',
            text: '<',
            flex: 0,
            disabled: true,
            listeners: {
                click: function() {
                    me.store.previousPage();
                }
            },
        });

        this.middleLabel = Ext.ComponentManager.create({
            xtype: 'component',
            html: '',
            style: {
                'text-align': 'center'
            },
            flex: 1,
            //width: 200
        });

        this.nextButton = Ext.ComponentManager.create({
            xtype: 'button',
            text: '>',
            flex: 0,
            disabled: true,
            listeners: {
                click: function() {
                    me.store.nextPage();
                }
            }
        });

        this.items = [
            this.previousButton,
            this.middleLabel,
            this.nextButton
        ];
        if(this.reverseDirection) {
            this.nextButton.setText('<');
            this.previousButton.setText('>');
            this.items[2] = this.previousButton;
            this.items[0] = this.nextButton;
        }
        this.callParent(arguments);

        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.updatePageSwitcher(records);
            }
        });
    },

    updatePageSwitcher: function(records) {
        if(records.length == 0) {
            this.hide();
            return;
        } else {
            this.show();
        }
        var from = this.store.pageSize * (this.store.currentPage-1);
        var visibleOnCurrentPage = this.store.getCount();
        var totalPages = this.store.getTotalCount() / this.store.pageSize;

        var label = this.middleLabelTpl.apply({
            total: this.store.getTotalCount(),
            from: from + 1,
            to: from + visibleOnCurrentPage,
            //records: records, // Enable if we need it anywhere
            firstRecord: records.length == 0? undefined: records[0],
            currentPage: this.store.currentPage,
            currentNegativePageOffset: totalPages - this.store.currentPage + 1
        });
        this.middleLabel.update(label);

        this.previousButton.disable();
        if(from > 0) {
            this.previousButton.enable();
        }
        this.nextButton.disable();
        if(visibleOnCurrentPage == this.store.pageSize && (from+visibleOnCurrentPage) != this.store.getTotalCount()) {
            this.nextButton.enable();
        }
    }
});
