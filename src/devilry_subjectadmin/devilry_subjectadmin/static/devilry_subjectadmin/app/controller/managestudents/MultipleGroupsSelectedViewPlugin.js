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
        'managestudents.SelectedGroupsSummaryGrid'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage',
        'devilry_subjectadmin.utils.Array',
        'Ext.window.Window'
    ],

    stores: ['SelectedGroups'],

    refs: [{
        ref: 'setExaminersPanel',
        selector: '#setExaminersWindow chooseexaminerspanel'
    }, {
        ref: 'addExaminersPanel',
        selector: '#addExaminersWindow chooseexaminerspanel'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsMultipleGroupsSelected: this._onMultipleGroupsSelected
        });
        this.control({
            'viewport multiplegroupsview': {
                render: this._onRender
            },
            'viewport multiplegroupsview #setExaminersButton': {
                click: this._onSetExaminers
            },
            '#setExaminersWindow chooseexaminerspanel': {
                addUser: this._onExaminerSetAdd,
                removeUsers: this._onExaminerSetRemove
            },
            'viewport multiplegroupsview #addExaminersButton': {
                click: this._onAddExaminers
            },
            '#addExaminersWindow chooseexaminerspanel': {
                addUser: this._onExaminerAddPanelAdd
            },
            'viewport multiplegroupsview selectedgroupssummarygrid #selectUsersByAutocompleteWidget': {
                userSelected: this._onUserSelectedByAutocomplete
            }
        });
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
    },

    _onRender: function() {
        //console.log('render MultipleGroupsSelectedView');
    },

    _createTopMessage: function() {
        var tpl = Ext.create('Ext.XTemplate', gettext('{numselected} {groupunit_plural} selected.'));
        return tpl.apply({
            numselected: this.groupRecords.length,
            groupunit_plural: this.manageStudentsController.getTranslatedGroupUnit(true)
        });
    },

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

    _syncExaminers: function(userStore, doNotDeleteUsers) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            var examiners = [];
            var currentExaminers = groupRecord.get('examiners');
            devilry_subjectadmin.utils.Array.mergeIntoArray({
                destinationArray: currentExaminers,
                sourceArray: userStore.data.items,
                isEqual: function(examiner, userRecord) {
                    return examiner.user.id == userRecord.get('id');
                },
                onMatch: function(examiner) {
                    examiners.push(examiner);
                },
                onNoMatch: function(examiner) {
                    if(doNotDeleteUsers) {
                        examiners.push(examiner);
                    }
                },
                onAdd: function(userRecord) {
                    examiners.push({
                        user: {id: userRecord.get('id')}
                    });
                }
            });
            groupRecord.set('examiners', examiners);
        }
    },

    _onExaminerSetAdd: function(addedUserRecord) {
        var userStore = this.getSetExaminersPanel().store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getSetExaminersPanel().afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },

    _onExaminerSetRemove: function(removedUserRecords) {
        var userStore = this.getSetExaminersPanel().store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getSetExaminersPanel().afterItemsRemovedSuccessfully(removedUserRecords);
            }
        });
    },

    _onExaminerAddPanelAdd: function(addedUserRecord) {
        var userStore = this.getAddExaminersPanel().store;
        this._syncExaminers(userStore, true);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getAddExaminersPanel().afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },

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

    _onUserSelectedByAutocomplete: function(combo, searchGroupRecord) {
        // NOTE: This searchGroupRecord is not from the same proxy as the records in the
        //       "regular" list, so their internal IDs do not match. Therefore,
        //       we use getRecordByGroupId() to get the correct receord.
        combo.clearValue();
        combo.focus();
        var groupId = searchGroupRecord.get('id');
        var groupRecord = this.manageStudentsController.getRecordByGroupId(groupId);
        if(groupRecord) {
            if(this.manageStudentsController.groupRecordIsSelected(groupRecord)) {
                this._showSelectSearchErrorMessage(combo, {
                    title: gettext('Already selected'),
                    msg: gettext('The group is already selected')
                });
            } else {
                this.manageStudentsController.selectGroupRecords([groupRecord], true);
            }
        } else {
            this._showSelectSearchErrorMessage(combo, {
                title: gettext('Selected group not loaded'),
                msg: gettext('The group you selected is not loaded. This is probably because someone else added a group after you loaded this page. Try reloading the page.')
            });
        }
    }
});
