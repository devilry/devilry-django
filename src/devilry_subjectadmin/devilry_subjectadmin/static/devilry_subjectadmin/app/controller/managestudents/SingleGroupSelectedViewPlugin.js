/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a single group when
 * it is selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.SingleGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage'
    ],

    models: [
        'Candidate',
        'Examiner',
        'Tag',
        'PopFromGroup'
    ],

    views: [
        'managestudents.SingleGroupSelectedView',
        'managestudents.SelectExaminersGrid'
    ],

    refs: [{
    // Students
        ref: 'studentsCardBody',
        selector: 'viewport singlegroupview managestudentsonsingle #cardBody'
    }, {

    // Examiners
        ref: 'examinersCardBody',
        selector: 'viewport singlegroupview manageexaminersonsingle #cardBody'
    }, {

    // Tags
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
            'viewport singlegroupview managestudentsonsingle studentsingroupgrid': {
                popStudent: this._onPopStudent
            },
            'viewport singlegroupview managestudentsonsingle okcancelpanel#confirmPop': {
                cancel: this._showStudentsDefaultView,
                ok: this._onPopStudentConfirmed
            },

            // Examiners
            'viewport singlegroupview manageexaminersonsingle examinersingroupgrid': {
                removeExaminer: this._onRemoveExaminer
            },
            'viewport singlegroupview manageexaminersonsingle okcancelpanel#confirmRemove': {
                cancel: this._showExaminersDefaultView,
                ok: this._onRemoveExaminerConfirmed
            },

            'viewport singlegroupview examinersingroupgrid #addExaminer': {
                click: this._onAddExaminerButtonClicked
            },
            //'viewport singlegroupview examinersingroupgrid #removeAllExaminers': {
                //click: this._onRemoveAllExaminers
            //},
            '#addExaminersOnSingleGroupWindow chooseexaminerspanel': {
                addUser: this._onAddExaminer
            },

            // Tags
            'viewport singlegroupview tagsingroupgrid #addTags': {
                click: this._onAddTags
            },
            '#addTagsOnSingleGroupWindow choosetagspanel': {
                cancel: this._onCancelTags,
                savetags: this._onSaveTags
            },
            'viewport singlegroupview tagsingroupgrid': {
                removeTag: this._onRemoveTag
            },
            'viewport singlegroupview tagsingroupgrid #removeAllTags': {
                click: this._onRemoveAllTags
            }
        });
        this.mon(this.getPopFromGroupModel().proxy, {
            scope: this,
            exception: this._onPopFromGroupProxyError
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
        return interpolate(gettext('Selecting multiple %(groups_term)s enables you to change %(examiners_term)s and %(tags_term)s on multiple %(groups_term)s, and merge multiple %(groups_term)s into a single %(group_term)s.'), {
            groups_term: gettext('groups'),
            examiners_term: gettext('examiners'),
            tags_term: gettext('tags'),
            group_term: gettext('group')
        }, true);
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
    _showStudentsDefaultView: function() {
        this.getStudentsCardBody().getLayout().setActiveItem('helpAndButtonsContainer');
    },

    _createStudentsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getCandidateModel(),
            data: this.groupRecord.get('candidates')
        });
        return store;
    },
    _onPopStudent: function(candidateRecord) {
        this.getStudentsCardBody().getLayout().setActiveItem('confirmPop');
        var confirmPanel = this.getStudentsCardBody().down('#confirmPop');
        confirmPanel.candidateRecord = candidateRecord; // NOTE: temporary storage - removed in _onPopStudentConfirmed()
    },
    _onPopStudentConfirmed: function() {
        var confirmPanel = this.getStudentsCardBody().down('#confirmPop');
        var candidateRecord = confirmPanel.candidateRecord;
        confirmPanel.candidateRecord = undefined;

        var assignmentRecord = this.manageStudentsController.assignmentRecord;
        var record = Ext.create('devilry_subjectadmin.model.PopFromGroup');
        record.proxy.setUrl(assignmentRecord.get('id'));
        record.set('group_id', this.groupRecord.get('id'));
        record.set('candidate_id', candidateRecord.get('id'));
        record.save({
            scope: this,
            callback: function(result, operation) {
                if(operation.success) {
                    this._onPopStudentSuccess(result);
                } else {
                    // NOTE: Errors are handled in _onPopFromGroupProxyError
                }
            }
        });
    },

    _onPopStudentSuccess: function(result) {
        var group_id = result.get('group_id');
        var new_group_id = result.get('new_group_id');
        this.manageStudentsController.reloadGroups([group_id, new_group_id]);
    },
    _onPopFromGroupProxyError: function(proxy, response, operation) {
        this.handleProxyUsingHtmlErrorDialog(response, operation);
    },



    /************************************************
     *
     * Examiners
     *
     ***********************************************/
    _showExaminersDefaultView: function() {
        this.getExaminersCardBody().getLayout().setActiveItem('helpAndButtonsContainer');
    },

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

    //_onRemoveAllExaminers: function() {
        //this._confirm({
            //title: gettext('Confirm clear examiners'),
            //msg: gettext('Do you want to remove all examiners from this group?'),
            //callback: this._removeAllExaminers
        //});
    //},
    //_removeAllExaminers: function() {
        //this.groupRecord.set('examiners', []);
        //this.manageStudentsController.notifySingleGroupChange();
    //},


    // Remove examiner

    _onRemoveExaminer: function(examinerRecord) {
        this.getExaminersCardBody().getLayout().setActiveItem('confirmRemove');
        var confirmPanel = this.getExaminersCardBody().down('#confirmRemove');
        confirmPanel.examinerRecord = examinerRecord; // NOTE: temporary storage - removed in _onPopExaminerConfirmed()
    },
    _onRemoveExaminerConfirmed: function() {
        var confirmPanel = this.getExaminersCardBody().down('#confirmRemove');
        var examinerRecord = confirmPanel.examinerRecord;
        confirmPanel.examinerRecord = undefined;

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

    _onCancelTags: function(panel) {
        panel.up('window').close();
    },

    _onSaveTags: function(panel, tags) {
        panel.up('window').close();
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
