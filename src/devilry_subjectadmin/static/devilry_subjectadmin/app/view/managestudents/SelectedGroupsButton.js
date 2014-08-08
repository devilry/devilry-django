/** A button that displays the number of selected groups in a grid, and shows
 * SelectedGroupsMenu when clicked. */
Ext.define('devilry_subjectadmin.view.managestudents.SelectedGroupsButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.selectedgroupsbutton',
    cls: 'devilry_subjectadmin_selectedgroupsbutton',
    requires: [
        'devilry_subjectadmin.view.managestudents.SelectedGroupsMenu',
        'Ext.XTemplate'
    ],

    textTpl: [
        gettext('{selected}/{total} selected')
    ],

    menuAlign: 'tr-br?',

    /**
     * @cfg {Object} [grid]
     * The grid to show selection for.
     */

    initComponent: function() {
        Ext.apply(this, {
            disabled: true,
            text: gettext('Loading') + ' ...',
            menu: {
                xtype: 'selectedgroupsmenu',
                grid: this.grid
            }
        });
        this.textTplCompiled = Ext.create('Ext.XTemplate', this.textTpl);
        this.mon(this.grid, {
            scope: this,
            selectionchange: this._onGridSelectionChange
        });
        this.callParent(arguments);

        var store = this.grid.getStore();
        this.mon(store, {
            scope: this,
            load: this._onStoreLoad
        });
        if(!store.isLoading()) {
            this._updateText(this.grid.getSelectionModel().getSelection());
        }
    },

    _onStoreLoad: function() {
        this._updateText(this.grid.getSelectionModel().getSelection());
    },


    _onGridSelectionChange: function(selModel, selectedGroupRecords) {
        if(selectedGroupRecords.length === 0) {
            this.disable();
        } else {
            this.enable();
        }
        this._updateText(selectedGroupRecords);
    },

    _updateText: function(selectedGroupRecords) {
        var store = this.grid.getStore();
        var total = store.getCount();
        this.setText(this.textTplCompiled.apply({
            selected: selectedGroupRecords.length,
            total: total
        }));
    }
});
