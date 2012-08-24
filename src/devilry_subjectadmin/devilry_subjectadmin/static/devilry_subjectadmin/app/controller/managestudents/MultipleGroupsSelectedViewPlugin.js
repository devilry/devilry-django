/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a multiple groups when
 * they are selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.MultipleGroupsSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.MultipleGroupsSelectedView',
        'managestudents.ChooseExaminersWindow',
        'managestudents.ChooseTagsWindow',
        'managestudents.SelectedGroupsSummaryGrid'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage',
        'devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup',
        'Ext.tip.ToolTip',
        'Ext.util.KeyNav'
    ],

    stores: ['SelectedGroups'],

    refs: [{
        ref: 'setTagsWindow',
        selector: '#setTagsWindow'
    }, {
        ref: 'addTagsWindow',
        selector: '#addTagsWindow'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsMultipleGroupsSelected: this._onMultipleGroupsSelected,
            managestudentsGroupSorterChanged: this._onGroupsSorterChanged
        });
        this.control({
            'viewport multiplegroupsview': {
                render: this._onRender
            },

            // setExaminers
            'viewport multiplegroupsview #setExaminersButton': {
                click: this._onSetExaminers
            },
            '#setExaminersWindow chooseexaminerspanel': {
                addUser: this._onExaminerSetAdd,
                removeUsers: this._onExaminerSetRemove
            },

            // addExaminers
            'viewport multiplegroupsview #addExaminersButton': {
                click: this._onAddExaminers
            },
            '#addExaminersWindow chooseexaminerspanel': {
                addUser: this._onExaminerAddPanelAdd
            },

            // clearExaminers
            'viewport multiplegroupsview #clearExaminersButton': {
                click: this._onClearExaminers
            },


            // setTags
            'viewport multiplegroupsview #setTagsButton': {
                click: this._onSetTags
            },
            '#setTagsWindow': {
                savetags: this._onSetTagsSave
            },

            // addTags
            'viewport multiplegroupsview #addTagsButton': {
                click: this._onAddTags
            },
            '#addTagsWindow': {
                savetags: this._onAddTagsSave
            },

            // clearTags
            'viewport multiplegroupsview #clearTagsButton': {
                click: this._onClearTags
            }
        });
    },

    _onGroupsSorterChanged: function(sorter) {
        var store = this.getSelectedGroupsStore();
        store.sortBySpecialSorter(sorter);
    },

    _onMultipleGroupsSelected: function(manageStudentsController, groupRecords) {
        this.groupRecords = groupRecords;
        this.manageStudentsController = manageStudentsController;
        this.manageStudentsController.setBody({
            xtype: 'multiplegroupsview',
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            topMessage: this._createTopMessage()
        });

        this._populateSelectedGroupsStore();
    },

    _populateSelectedGroupsStore: function() {
        var store = this.getSelectedGroupsStore();
        //Ext.Array.each(this.groupRecords, function(groupRecord, index) {
            //console.log(groupRecord, 'loaded');
            //store.add(groupRecord);
        //}, this);
        store.removeAll();
        store.loadData(this.groupRecords);
        store.sortBySpecialSorter(this.manageStudentsController.getCurrentGroupsStoreSorter());
    },

    _onRender: function() {
        //console.log('render MultipleGroupsSelectedView');
    },

    _createTopMessage: function() {
        return interpolate(gettext('%(numselected)s/%(total)s %(groups_term)s selected.'), {
            numselected: this.groupRecords.length,
            total: this.manageStudentsController.getTotalGroupsCount(),
            groups_term: gettext('groups')
        }, true);
    },



    /************************************************
     *
     * Set examiners
     *
     ************************************************/


    _onSetExaminers: function() {
        Ext.widget('chooseexaminerswindow', {
            title: gettext('Set examiners'),
            itemId: 'setExaminersWindow',
            panelConfig: {
                includeRemove: true,
                sourceStore: this.manageStudentsController.getRelatedExaminersRoStore()
            }
        }).show();
    },

    _onAddExaminers: function() {
        Ext.widget('chooseexaminerswindow', {
            title: gettext('Add examiners'),
            itemId: 'addExaminersWindow',
            panelConfig: {
                sourceStore: this.manageStudentsController.getRelatedExaminersRoStore()
            }
        }).show();
    },

    _onClearExaminers: function() {
        Ext.MessageBox.show({
            title: gettext('Confirm clear examiners'),
            msg: gettext('Do you want to remove all examiners from the selected groups? Their existing feedback will not be removed, only their permission to give feedback on the groups.'),
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            scope: this,
            fn: function(buttonid) {
                if(buttonid == 'yes') {
                    this._clearExaminers();
                }
            }
        });
    },

    _clearExaminers: function() {
        Ext.Array.each(this.groupRecords, function(groupRecord) {
            groupRecord.set('examiners', []);
        }, this);
        this.manageStudentsController.notifyMultipleGroupsChange();
    },

    _syncExaminers: function(userStore, doNotDeleteUsers) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            var userRecords = userStore.data.items;
            devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeExaminers({
                groupRecord: groupRecord,
                userRecords: userRecords,
                doNotDeleteUsers: doNotDeleteUsers
            });
        }
    },

    _onExaminerSetAdd: function(addedUserRecord, panel) {
        var userStore = panel.store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                panel.afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },

    _onExaminerSetRemove: function(removedUserRecords, panel) {
        var userStore = panel.store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                panel.afterItemsRemovedSuccessfully(removedUserRecords);
            }
        });
    },

    _onExaminerAddPanelAdd: function(addedUserRecord, panel) {
        var userStore = panel.store;
        this._syncExaminers(userStore, true);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                panel.afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },




    /************************************************
     *
     * Set tags
     *
     ************************************************/

    _syncTags: function(sourceTags, doNotDeleteTags) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeTags({
                groupRecord: groupRecord,
                sourceTags: sourceTags,
                doNotDeleteTags: doNotDeleteTags
            });
        }
    },


    // Set tags

    _onSetTags: function() {
        Ext.widget('choosetagswindow', {
            title: gettext('Set tags'),
            itemId: 'setTagsWindow',
            buttonText: gettext('Set tags')
        }).show();
    },

    _onSetTagsSave: function(win, tags) {
        win.close();
        this._syncTags(tags);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
            }
        });
    },

    // Add tags

    _onAddTagsSave: function(win, tags) {
        win.close();
        this._syncTags(tags, true);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
            }
        });
    },

    _onAddTags: function() {
        Ext.widget('choosetagswindow', {
            title: gettext('Add tags'),
            itemId: 'addTagsWindow',
            buttonText: gettext('Add tags')
        }).show();
    },


    // Clear tags

    _onClearTags: function() {
        Ext.MessageBox.show({
            title: gettext('Confirm clear tags'),
            msg: gettext('Do you want to remove all tags from the selected groups?'),
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            scope: this,
            fn: function(buttonid) {
                if(buttonid == 'yes') {
                    this._clearTags();
                }
            }
        });
    },

    _clearTags: function() {
        Ext.Array.each(this.groupRecords, function(groupRecord) {
            groupRecord.set('tags', []);
        }, this);
        this.manageStudentsController.notifyMultipleGroupsChange();
    }
});
