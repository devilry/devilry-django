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
        'Ext.util.KeyMap',
        'Ext.util.MixedCollection'
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

            // By grade
            'viewport managestudentsoverview #selectGradeFailed': {
                click: this._onSelectGradeFailed
            },
            'viewport managestudentsoverview #selectGradePassed': {
                click: this._onSelectGradePassed
            },

            // By deliveries
            'viewport managestudentsoverview #selectHasDeliveries': {
                click: this._onSelectHasDeliveries
            },
            'viewport managestudentsoverview #selectNoDeliveries': {
                click: this._onSelectNoDeliveries
            },

            // By examiners
            'viewport managestudentsoverview #selectHasExaminer': {
                click: this._onSelectHasExaminer
            },
            'viewport managestudentsoverview #selectNoExaminer': {
                click: this._onSelectNoExaminer
            },
            'viewport managestudentsoverview #specificExaminerMenu': {
                show: this._onShowSpecificExaminerMenu
            },
            'viewport managestudentsoverview #specificExaminerMenu menuitem': {
                click: this._onSpecificExaminerMenuItemClick
            },

            // By tags
            'viewport managestudentsoverview #selectHasTag': {
                click: this._onSelectHasTag
            },
            'viewport managestudentsoverview #selectNoTag': {
                click: this._onSelectNoTag
            },
            'viewport managestudentsoverview #specificTagMenu': {
                show: this._onShowSpecificTagMenu
            },
            'viewport managestudentsoverview #specificTagMenu menuitem': {
                click: this._onSpecificTagMenuItemClick
            }
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


    // 
    // Status
    //

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


    //
    // Grade
    //

    _onSelectGradeFailed: function(button) {
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback && !feedback.is_passing_grade;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectGradePassed: function(button) {
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback && feedback.is_passing_grade;
        }, this, this._isInAddToSelectionMenu(button));
    },


    // 
    // Deliveries
    //

    _onSelectHasDeliveries: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('num_deliveries') > 0;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectNoDeliveries: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('num_deliveries') == 0;
        }, this, this._isInAddToSelectionMenu(button));
    },


    //
    // Examiners
    //

    _onSelectHasExaminer: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('examiners').length > 0;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectNoExaminer: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('examiners').length == 0;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificExaminerMenu: function(menu) {
        // Add unique users, and count groups
        var examinerMap = new Ext.util.MixedCollection(); // userid -> {user: userObj, count: COUNT, name: NAME}
        this.getGroupsStore().each(function(groupRecord) {
            var examiners = groupRecord.get('examiners');
            for(var index=0; index<examiners.length; index++)  {
                var examiner = examiners[index];
                var userid = examiner.user.id;
                if(examinerMap.containsKey(userid)) {
                    examinerMap.get(userid).count ++;
                } else {
                    var name = examiner.user.full_name || examiner.user.username || Ext.String.format('User ID: ', examiner.user.id);
                    examinerMap.add(userid, {
                        user: examiner.user,
                        name: name,
                        count: 1
                    });
                }
            }
        }, this);
        
        // Sort
        examinerMap.sortBy(function(a, b) {
            return a.name.localeCompare(b.name);
        });

        // Create and set items
        var items = [];
        examinerMap.each(function(examiner) {
            items.push({
                itemId: Ext.String.format('selectByExaminerUserId_{0}', examiner.user.id),
                text: Ext.String.format('{0} ({1})', examiner.name, examiner.count)
            });
        });
        menu.setItems(items);
    },

    _onSpecificExaminerMenuItemClick: function(button) {
        var userid = parseInt(button.itemId.split('_')[1]);
        this._selectBy(function(groupRecord) {
            return groupRecord.hasExaminer(userid);
        }, this, this._isInAddToSelectionMenu(button));
    },



    //
    //Tags
    //

    _onSelectHasTag: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('tags').length > 0;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectNoTag: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('tags').length == 0;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificTagMenu: function(menu) {
        // Add unique tags, and count groups
        var tagMap = new Ext.util.MixedCollection(); // TAG -> {tag: TAG, count: COUNT}
        this.getGroupsStore().each(function(groupRecord) {
            var tags = groupRecord.get('tags');
            for(var index=0; index<tags.length; index++)  {
                var tagObj = tags[index];
                if(tagMap.containsKey(tagObj.tag)) {
                    tagMap.get(tagObj.tag).count ++;
                } else {
                    tagMap.add(tagObj.tag, {
                        tag: tagObj.tag,
                        count: 1
                    });
                }
            }
        }, this);
        
        // Sort
        tagMap.sortBy(function(a, b) {
            return a.tag.localeCompare(b.tag);
        });

        // Create and set items
        var items = [];
        tagMap.each(function(tag) {
            items.push({
                itemId: Ext.String.format('selectByTag_{0}', tag.tag),
                text: Ext.String.format('{0} ({1})', tag.tag, tag.count)
            });
        });
        menu.setItems(items);
    },

    _onSpecificTagMenuItemClick: function(button) {
        var tag = button.itemId.split('_')[1];
        console.log(tag);
        this._selectBy(function(groupRecord) {
            return groupRecord.hasTag(tag);
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
