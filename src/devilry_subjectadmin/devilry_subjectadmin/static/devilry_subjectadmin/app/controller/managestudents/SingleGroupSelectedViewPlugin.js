/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a single group when
 * it is selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.SingleGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    requires: [
        'devilry_extjsextras.AlertMessage'
    ],

    models: [
        'Candidate',
        'Examiner',
        'Tag'
    ],

    views: [
        'managestudents.SingleGroupSelectedView',
        'managestudents.ChooseExaminersWindow',
        'managestudents.ChooseTagsWindow'
    ],

    refs: [{
        ref: 'addTagsOnSingleGroupWindow',
        selector: '#addTagsOnSingleGroupWindow'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSingleGroupSelected: this._onSingleGroupSelected
        });
        this.control({
            'viewport singlegroupview': {
                render: this._onRender
            },

            // Students
            'viewport singlegroupview studentsingroupgrid': {
                removeStudent: this._onRemoveStudent
            },

            // Examiners
            'viewport singlegroupview examinersingroupgrid': {
                removeExaminer: this._onRemoveExaminer
            },
            'viewport singlegroupview examinersingroupgrid #addExaminer': {
                click: this._onAddExaminerButtonClicked
            },
            'viewport singlegroupview examinersingroupgrid #removeAllExaminers': {
                click: this._onRemoveAllExaminers
            },
            '#addExaminersOnSingleGroupWindow chooseexaminerspanel': {
                addUser: this._onAddExaminer
            },

            // Tags
            'viewport singlegroupview tagsingroupgrid #addTags': {
                click: this._onAddTags
            },
            '#addTagsOnSingleGroupWindow': {
                savetags: this._onSaveTags
            },
            'viewport singlegroupview tagsingroupgrid': {
                removeTag: this._onRemoveTag
            },
            'viewport singlegroupview tagsingroupgrid #removeAllTags': {
                click: this._onRemoveAllTags
            }
        });
    },

    _onSingleGroupSelected: function(manageStudentsController, groupRecord) {
        this.manageStudentsController = manageStudentsController;
        this.groupRecord = groupRecord;
        this._refreshBody();
    },

    _refreshBody: function() {
        this.manageStudentsController.setBody({
            xtype: 'singlegroupview',
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            multiselectWhy: this._getMultiSelectWhy(),
            studentsStore: this._createStudentsStore(),
            examinersStore: this._createExaminersStore(),
            tagsStore: this._createTagsStore(),
            groupRecord: this.groupRecord
        });
    },

    _onRender: function() {
        //console.log('render SingleGroupSelectedView');
    },

    _getMultiSelectWhy: function() {
        return Ext.create('Ext.XTemplate', gettext('Selecting multiple {groupunit_plural} enables you to change examiners and tags on multiple students, and organize students in project groups.')).apply({
            groupunit_plural: this.manageStudentsController.getTranslatedGroupUnit(true)
        });
    },

    _confirm: function(config) {
        Ext.MessageBox.show({
            title: config.title,
            msg: config.msg,
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            scope: this,
            fn: function(buttonid) {
                if(buttonid == 'yes') {
                    Ext.callback(config.callback, this);
                }
            }
        });
    },


    /************************************************
     *
     * Students
     *
     ***********************************************/

    _createStudentsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getCandidateModel(),
            data: this.groupRecord.get('candidates')
        });
        return store;
    },
    _onRemoveStudent: function(candidateRecord) {
        Ext.MessageBox.alert('Not implemented', 'See <a href="https://github.com/devilry/devilry-django/issues/215" target="_blank">issue 215</a> for info about how this will work.');
        //console.log('Remove student:', candidateRecord.data);
    },



    /************************************************
     *
     * Examiners
     *
     ***********************************************/

    _createExaminersStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getExaminerModel(),
            data: this.groupRecord.get('examiners')
        });
        return store;
    },
    _onAddExaminerButtonClicked: function() {
        Ext.widget('chooseexaminerswindow', {
            title: gettext('Add examiners'),
            itemId: 'addExaminersOnSingleGroupWindow',
            panelConfig: {
                sourceStore: this.manageStudentsController.getRelatedExaminersRoStore()
            }
        }).show();
    },
    _onAddExaminer: function(addedUserRecord, panel) {
        var userStore = panel.store;
        devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeExaminers({
            groupRecord: this.groupRecord,
            userRecords: userStore.data.items,
            doNotDeleteUsers: true
        });
        this.manageStudentsController.notifySingleGroupChange({
            scope: this,
            success: function() {
                panel.afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },
    

    // Remove all examiners

    _onRemoveAllExaminers: function() {
        this._confirm({
            title: gettext('Confirm clear examiners'),
            msg: gettext('Do you want to remove all examiners from this group?'),
            callback: this._removeAllExaminers
        });
    },
    _removeAllExaminers: function() {
        this.groupRecord.set('examiners', []);
        this.manageStudentsController.notifySingleGroupChange();
    },


    // Remove examiner

    _onRemoveExaminer: function(examinerRecord) {
        this._confirm({
            title: gettext('Confirm remove examiner'),
            msg: Ext.String.format(gettext('Do you want to remove "{0}" from examiners?'), examinerRecord.get('user').username),
            callback: function() {
                this._removeExaminer(examinerRecord);
            }
        });
    },

    _removeExaminer: function(examinerRecord) {
        devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.removeExaminers({
            groupRecord: this.groupRecord,
            userRecords: [examinerRecord],
            getUserId: function(examinerRecord) {
                return examinerRecord.get('user').id;
            }
        });
        this.manageStudentsController.notifySingleGroupChange();
    },



    /***********************************************
     *
     * Tags
     *
     **********************************************/

    _createTagsStore: function() {
        //console.log(this.groupRecord.data);
        var store = Ext.create('Ext.data.Store', {
            model: this.getTagModel(),
            data: this.groupRecord.get('tags')
        });
        return store;
    },

    // Add tags

    _onAddTags: function() {
        Ext.widget('choosetagswindow', {
            title: gettext('Add tags'),
            itemId: 'addTagsOnSingleGroupWindow',
            buttonText: gettext('Add tags')
        }).show();
    },

    _onSaveTags: function(win, tags) {
        win.close();
        devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeTags({
            groupRecord: this.groupRecord,
            sourceTags: tags,
            doNotDeleteTags: true
        });
        this.manageStudentsController.notifySingleGroupChange();
    },


    // Remove all tags

    _onRemoveAllTags: function() {
        this._confirm({
            title: gettext('Confirm clear tags'),
            msg: gettext('Do you want to remove all tags from this group?'),
            callback: this._removeAllTags
        });
    },
    _removeAllTags: function() {
        this.groupRecord.set('tags', []);
        this.manageStudentsController.notifySingleGroupChange();
    },


    // Remove tag

    _onRemoveTag: function(tagRecord) {
        this._confirm({
            title: gettext('Confirm remove tag'),
            msg: Ext.String.format(gettext('Do you want to remove "{0}" from tags?'), tagRecord.get('tag')),
            callback: function() {
                this._removeTag(tagRecord);
            }
        });
    },

    _removeTag: function(tagRecord) {
        devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.removeTags({
            groupRecord: this.groupRecord,
            sourceTags: [tagRecord.get('tag')]
        });
        this.manageStudentsController.notifySingleGroupChange();
    }
});
