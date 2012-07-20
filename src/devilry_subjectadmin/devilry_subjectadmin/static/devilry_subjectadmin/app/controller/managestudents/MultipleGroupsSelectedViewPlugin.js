/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a multiple groups when
 * they are selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.MultipleGroupsSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.MultipleGroupsSelectedView',
        'managestudents.ChooseExaminersWindow'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage',
        'devilry_subjectadmin.utils.Array',
        'Ext.window.Window'
    ],

    refs: [{
        ref: 'setExaminersPanel',
        selector: '#setExaminersWindow chooseexaminerspanel'
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
            itemId: 'setExaminersWindow'
        }).show();
    },

    _syncExaminers: function(userStore) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            var examiners = [];
            devilry_subjectadmin.utils.Array.mergeIntoArray({
                destinationArray: groupRecord.get('examiners'),
                sourceArray: userStore.data.items,
                isEqual: function(examiner, userRecord) {
                    return examiner.user.id == userRecord.get('id');
                },
                onMatch: function(examiner, userRecord) {
                    examiners.push(examiner);
                },
                //onNoMatch: function(destIndex) {
                //},
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
        //for(var i=0; i<this.groupRecords.length; i++)  {
            //var groupRecord = this.groupRecords[i];
            //console.log(groupRecord.debugFormat());
        //}
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getSetExaminersPanel().onUserAdded(addedUserRecord);
            }
        });
    },

    _onExaminerSetRemove: function(removedUserRecords) {
        var userStore = this.getSetExaminersPanel().store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getSetExaminersPanel().onUsersRemoved(removedUserRecords);
            }
        });
    }
});
