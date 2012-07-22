/**
 * Controller for the select buttons and select by search field.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.Select', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.ListOfGroups',
        'managestudents.AutocompleteGroupWidget'
    ],

    requires: [
        'Ext.util.KeyMap'
    ],

    stores: [
        'Groups'
    ],


    /**
     * Get the main view for managestudents.
     * @return {devilry_subjectadmin.view.managestudents.Overview} The overview.
     * @method getOverview
     */

    refs: [{
        ref: 'listOfGroups',
        selector: 'listofgroups'
    }],

    init: function() {
        this.control({
            'viewport managestudentsoverview listofgroups': {
                render: this._onRenderListOfGroups
            },
            'viewport multiplegroupsview selectedgroupssummarygrid': {
                beforeselect: this._onSelectGroupInSummaryGrid
            },
            'viewport #selectUsersByAutocompleteWidget': {
                userSelected: this._onUserSelectedBySearch
            },

            'viewport managestudentsoverview #selectButton #selectall': {
                click: this._onSelectAll
            },
            'viewport managestudentsoverview #selectButton #deselectall': {
                click: this._onDeselectAll
            },
            'viewport managestudentsoverview #selectButton #invertselection': {
                click: this._onInvertselection
            },
            
            // NOTE: The listeners below are shared by items in both
            //       #replaceSelectionMenu and #addToSelectionMenu.
            //       We use the itemId of their menu to determine if we want to
            //       keepExisting or not. See _isInAddToSelectionMenu()

            // By status
            'viewport managestudentsoverview #selectStatusOpen': {
                click: this._onSelectStatusOpen
            },
            'viewport managestudentsoverview #selectStatusClosed': {
                click: this._onSelectStatusClosed
            },
        });
    },

    _onRenderListOfGroups: function() {
        var map = new Ext.util.KeyMap(this.getListOfGroups().getEl(), {
            key: 'a',
            ctrl: true,
            fn: this._onSelectAll,
            scope: this
        });
    },


    /************************************************
     *
     * The multiselect summary grid
     *
     ************************************************/

    _onSelectGroupInSummaryGrid: function(rowmodel, selectedGroupRecord) {
        // NOTE: This selectedGroupRecord is not from the same proxy as the records in the
        //       "regular" list, so their internal IDs do not match. Therefore,
        //       we use _getGroupRecordById() to get the correct receord.
        var groupId = selectedGroupRecord.get('id');
        var groupRecord = this._getGroupRecordById(groupId);
        // NOTE: We defer deselecting to ensure that we return ``false`` before
        //       deselecting. If we deselect before returning, the grid will be gone
        //       when we return, and that causes an exception.
        Ext.defer(function() {
            this._deselectGroupRecords([groupRecord]);
        }, 10, this);
        return false;
    },



    /**************************************************
     *
     * Select by search
     *
     **************************************************/

    _showSelectSearchErrorMessage: function(combo, options) {
        Ext.MessageBox.show({
            title: options.title,
            msg: options.msg,
            buttons: Ext.MessageBox.OK,
            icon: Ext.MessageBox.ERROR,
            fn: function() {
                Ext.defer(function() {
                    combo.focus();
                }, 100);
            }
        });
    },

    _onUserSelectedBySearch: function(combo, searchGroupRecord) {
        // NOTE: This searchGroupRecord is not from the same proxy as the records in the
        //       "regular" list, so their internal IDs do not match. Therefore,
        //       we use _getGroupRecordById() to get the correct receord.
        combo.clearValue();
        combo.focus();
        var groupId = searchGroupRecord.get('id');
        var groupRecord = this._getGroupRecordById(groupId);
        if(groupRecord) {
            if(this._groupRecordIsSelected(groupRecord)) {
                this._showSelectSearchErrorMessage(combo, {
                    title: gettext('Already selected'),
                    msg: gettext('The group is already selected')
                });
            } else {
                this._selectGroupRecords([groupRecord], true);
            }
        } else {
            this._showSelectSearchErrorMessage(combo, {
                title: gettext('Selected group not loaded'),
                msg: gettext('The group you selected is not loaded. This is probably because someone else added a group after you loaded this page. Try reloading the page.')
            });
        }
    },


    /***********************************************
     *
     * Select menu button handlers
     *
     **********************************************/

    _onSelectAll: function() {
        this.getListOfGroups().getSelectionModel().selectAll();
    },
    _onDeselectAll: function() {
        this.getListOfGroups().getSelectionModel().deselectAll();
    },
    _onInvertselection: function() {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        var selected = Ext.clone(selectionModel.selected.items);

        // Add listener to the "next" selectionchange event, and trigger the selectionchange with selectAll
        this.getListOfGroups().on({
            selectionchange: function() {
                this._deselectGroupRecords(selected);
            },
            scope: this,
            single: true
        });
        this.getListOfGroups().getSelectionModel().selectAll();
    },


    _isInAddToSelectionMenu: function(button) {
        return button.up('#replaceSelectionMenu') == undefined;
    },

    _onSelectStatusOpen: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('is_open') == true;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectStatusClosed: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('is_open') == false;
        }, this, this._isInAddToSelectionMenu(button));
    },


    /***************************************************
     *
     * Methods to simplify selecting users
     *
     **************************************************/

    _findGroupRecordsBy: function(fn, scope) {
        var groupRecords = [];
        this.getGroupsStore().each(function(groupRecord) {
            var match = Ext.bind(fn, scope)(groupRecord);
            if(match) {
                groupRecords.push(groupRecord);
            }
        }, this);
        return groupRecords;
    },

    _selectBy: function(fn, scope, keepExisting) {
        var groupRecords = this._findGroupRecordsBy(fn, scope);
        this._selectGroupRecords(groupRecords, keepExisting);
    },

    /** Select the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * @param {Boolean} [keepExisting=false] True to retain existing selections
     * */
    _selectGroupRecords: function(groupRecords, keepExisting) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.select(groupRecords, keepExisting);
    },

    /** Deselect the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * */
    _deselectGroupRecords: function(groupRecords) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.deselect(groupRecords);
    },

    /** Get group record by group id.
     * @param {int} [groupId] The group id.
     * @return {devilry_subjectadmin.model.Group} The group record, or ``undefined`` if it is not found.
     * */
    _getGroupRecordById: function(groupId) {
        var index = this.getGroupsStore().findExact('id', groupId);
        if(index == -1) {
            return undefined;
        }
        return this.getGroupsStore().getAt(index);
    },

    /** Return ``true`` if ``groupRecord`` is selected. */
    _groupRecordIsSelected: function(groupRecord) {
        return this.getListOfGroups().getSelectionModel().isSelected(groupRecord);
    }
});
