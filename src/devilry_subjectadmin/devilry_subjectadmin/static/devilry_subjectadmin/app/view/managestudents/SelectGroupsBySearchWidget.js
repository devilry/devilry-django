Ext.define('devilry_subjectadmin.view.managestudents.SelectGroupsBySearchWidget', {
    extend: 'devilry_subjectadmin.view.managestudents.AutocompleteGroupWidget',
    alias: 'widget.selectgroupsbysearch',

    hideLabel: true,
    emptyText: gettext('Search (adds to selection)') + ' ...',

    /**
     * @cfg {Object} [grid]
     * The grid to select rows in when a searchitem is selected.
     */

    initComponent: function() {
        this.callParent(arguments);
        this.on({
            userSelected: this._onUserSelectedBySearch
        });
    },

    _onUserSelectedBySearch: function(combo, searchGroupRecord) {
        // NOTE: This searchGroupRecord is not from the same proxy as the records in the
        //       "regular" list, so their internal IDs do not match. Therefore,
        //       we use _getGroupRecordById() to get the correct receord.
        this.clearValue();
        this.focus();
        var groupId = searchGroupRecord.get('id');
        var groupRecord = this._getGroupRecordById(groupId);
        if(groupRecord) {
            if(this._groupRecordIsSelected(groupRecord)) {
                this._showSelectSearchErrorMessage({
                    title: gettext('Already selected'),
                    msg: gettext('The group is already selected')
                });
            } else {
                this._selectGroupRecords([groupRecord], true);
            }
        } else {
            this._showSelectSearchErrorMessage({
                title: gettext('Selected group not loaded'),
                msg: gettext('The group you selected is not loaded. This is probably because someone else added a group after you loaded this page. Try reloading the page.')
            });
        }
    },

    _getGroupRecordById: function(groupId) {
        var store = this.grid.getStore();
        var index = store.findExact('id', groupId);
        if(index == -1) {
            return undefined;
        }
        return store.getAt(index);
    },

    _selectGroupRecords: function(groupRecords, keepExisting) {
        var selectionModel = this.grid.getSelectionModel();
        selectionModel.select(groupRecords, keepExisting);
    },

    _groupRecordIsSelected: function(groupRecord) {
        return this.grid.getSelectionModel().isSelected(groupRecord);
    },

    _showSelectSearchErrorMessage: function(options) {
        var me = this;
        Ext.MessageBox.show({
            title: options.title,
            msg: options.msg,
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.ERROR,
            fn: function() {
                Ext.defer(function() {
                    me.focus();
                }, 200);
            }
        });
    }
});
