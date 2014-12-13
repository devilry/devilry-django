Ext.define('devilry_extjsextras.ManageItemsPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.manageitemspanel',

    /**
     * @cfg {Ext.data.Store} store
     * The store where items are added/deleted by this panel. Used for the
     * grid.
     */

    /**
     * @cfg [{Object}] columns
     * Grid columns.
     */

    /**
     * @cfg {boolean} confirmBeforeRemove
     * Show confirm dialog on remove? Defaults to ``true``.
     */
    confirmBeforeRemove: true,

    /**
     * @cfg {bool} hideHeaders
     * Hide grid headers?
     */
    hideHeaders: true,


    /**
     * @cfg {boolean} includeRemove
     * Include remove and selectall buttons.
     */

    /**
     * @cfg {Function} [filterFunction]
     * Callback used by the filter field. Return ``true`` on match.
     * If this is not included, no filter field is shown.
     */


    constructor: function(config) {
        config.cls = config.cls || this.cls || '';
        config.cls += ' devilry_extjsextras_manageitemspanel';
        this.addEvents({
            /**
             * @event
             * Fired to signal that a item should be added.
             * @param {[object]} itemRecord A item record.
             * */
            "addItem" : true,

            /**
             * @event
             * Fired to signal that items should be removed.
             * @param {[object]} itemRecords Array of item records.
             * */
            "removeItems" : true

        });

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);
    },

    initComponent: function() {
        var me = this;
        this.prettyFormatItemTplCompiled = Ext.create('Ext.XTemplate', this.prettyFormatItemTpl);

        Ext.apply(this, {
            frame: false,
            border: 0,
            layout: 'fit',
            items: [{
                xtype: 'grid',
                hideHeaders: this.hideHeaders,
                multiSelect: true,
                store: this.store,
                columns: this.columns,
                listeners: {
                    scope: this,
                    selectionchange: this._onGridSelectionChange
                }
            }]
        });

        var tbar = [];
        if(this.includeRemove) {
            tbar.push({
                xtype: 'button',
                cls: 'selectAllButton',
                text: gettext('Select all'),
                listeners: {
                    scope: this,
                    click: this._onSelectAll
                }
            });
            tbar.push({
                xtype: 'button',
                text: gettext('Remove'),
                itemId: 'removeButton',
                cls: 'removeButton',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onRemoveItemsClicked
                }
            });
        }
        if(this.filterFunction) {
            tbar.push({
                xtype: 'textfield',
                cls: 'filterfield',
                emptyText: gettext('Filter ...'),
                listeners: {
                    scope: this,
                    change: this._onFilterChange
                }
            });
        }
        if(tbar.length > 0) {
            this.tbar = tbar;
        }

        this.callParent(arguments);
    },

    /** Show savemask. */
    saveMask: function() {
        this.setLoading(gettext('Saving ...'))
    },

    /** Remove the save mask */
    removeSaveMask: function() {
        this.setLoading(false);
    },


    /** Use this to tell the user that the added user is already in the list.
     * @param callbackConfig
     *      Configures the callback function to invoke after the messagebox is closed.
     *      Attributes: ``callback`` and ``scope``.
     * */
    showDuplicateItemMessage: function(callbackConfig) {
        Ext.MessageBox.show({
            title: gettext('Already in list'),
            msg: gettext('The selected item is already in the list'),
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.ERROR,
            fn: function() {
                Ext.callback(callbackConfig.callback, callbackConfig.scope);
            }
        });
    },



    /*
     * 
     * Remove
     *
     */

    _getSelectedItems: function() {
        return this.down('grid').getSelectionModel().getSelection();
    },

    _onRemoveItemsClicked: function() {
        var selectedItems = this._getSelectedItems();
        if(this.confirmBeforeRemove) {
            this._confirmRemove(selectedItems);
        } else {
            this._removeItems(selectedItems);
        }
    },

    _removeItems: function(selectedItems) {
        this.saveMask();
        this.fireEvent('removeItems', selectedItems);
    },

    _confirmRemove: function(selectedItems) {
        var confirmMessage = gettext('Do you really want to remove the {numselected} selected items from the list?');
        Ext.MessageBox.show({
            title: gettext('Confirm remove'),
            msg: Ext.create('Ext.XTemplate', confirmMessage).apply({
                numselected: selectedItems.length
            }),
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this._removeItems(selectedItems);
                }
            },
            scope: this
        });
    },


    /*
     *
     * Select
     *
     */

    _onSelectAll: function() {
        this.down('grid').getSelectionModel().selectAll();
    },

    _onGridSelectionChange: function(selectionmodel) {
        if(this.includeRemove) {
            if(selectionmodel.getSelection().length == 0) {
                this.down('#removeButton').disable();
            } else {
                this.down('#removeButton').enable();
            }
        }
    },


    /*
     *
     * Filter
     *
     */

    _onFilterChange: function(filterfield, newValue, oldValue) {
        if(newValue === '') {
            this.store.clearFilter();
        } else {
            this._filter(newValue);
        }
    },

    _filter: function(query) {
        this.store.filterBy(function(record) {
            return this.filterFunction(query, record);
        }, this);
    },



    /** Should be called when save is complete. */
    selectRecord: function(record) {
        this.down('grid').getSelectionModel().select([record]);
    },

    /** Call this after an item has been added successfully.
     * */
    afterItemAddedSuccessfully: function(record) {
        this.selectRecord(record);
        this.removeSaveMask();
    },

    /** Call this after items have been removed successfully.
     * Typically called from the ``removeItems`` event handler.
     * */
    afterItemsRemovedSuccessfully: function(removedRecords) {
        this.removeSaveMask();
    },


    clearAndfocusField: function(selector) {
        var field = this.down(selector);
        Ext.defer(function() {
            field.clearValue();
            field.focus();
        }, 200);
    },


    /*
     *
     * Static functions
     *
     */

    statics: {
        caseIgnoreContains: function(fieldvalue, query) {
            if(fieldvalue) {
                return fieldvalue.toLocaleLowerCase().indexOf(query) > -1;
            } else {
                return false;
            }
        }
    }
});
