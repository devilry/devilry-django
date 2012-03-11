/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a single group when
 * it is selected.
 */
Ext.define('subjectadmin.controller.managestudents.SingleGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.AlertMessage'
    ],

    models: [
        'Candidate',
        'Examiner',
        'Tag'
    ],

    views: [
        'managestudents.SingleGroupSelectedView'
    ],

    //refs: [{
        //ref: '',
        //selector: 'singlegroupview'
    //}],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSingleGroupSelected: this._onSingleGroupSelected
        });
        this.control({
            'viewport singlegroupview': {
                render: this._onRender
            },
            'viewport singlegroupview studentsingroupgrid': {
                removeStudent: this._onRemoveStudent
            },

            'viewport singlegroupview examinersingroupgrid': {
                removeExaminer: this._onRemoveExaminer
            },
            'viewport singlegroupview examinersingroupgrid #addExaminer': {
                click: this._onAddExaminer
            },
            'viewport singlegroupview examinersingroupgrid #removeAllExaminers': {
                click: this._onRemoveAllExaminers
            },

            'viewport singlegroupview tagsingroupgrid': {
                removeTag: this._onRemoveTag
            },
            'viewport singlegroupview tagsingroupgrid #addTag': {
                click: this._onAddTag
            },
            'viewport singlegroupview tagsingroupgrid #removeAllTags': {
                click: this._onRemoveAllTags
            }
        });
    },

    _onSingleGroupSelected: function(manageStudentsController, groupRecord) {
        this.manageStudentsController = manageStudentsController;
        this.groupRecord = groupRecord;
        this.manageStudentsController.setBody({
            xtype: 'singlegroupview',
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            studentsStore: this._createStudentsStore(),
            examinersStore: this._createExaminersStore(),
            tagsStore: this._createTagsStore(),
            groupRecord: groupRecord
        });
    },

    _onRender: function() {
        //console.log('render SingleGroupSelectedView');
    },

    _createStudentsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getCandidateModel(),
            data: this.groupRecord.get('students')
        });
        return store;
    },
    _onRemoveStudent: function(candidateRecord) {
        alert('Not implemented.');
        console.log('Remove student:', candidateRecord.data);
    },


    _createExaminersStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getExaminerModel(),
            data: this.groupRecord.get('examiners')
        });
        return store;
    },
    _onAddExaminer: function() {
        alert('Not implemented.');
    },
    _onRemoveAllExaminers: function() {
        alert('Not implemented.');
    },
    _onRemoveExaminer: function(examinerRecord) {
        console.log('Remove examiner:', examinerRecord.data);
        alert('Not implemented.');
    },

    _createTagsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getTagModel(),
            data: this.groupRecord.get('tags')
        });
        return store;
    },
    _onAddTag: function() {
        alert('Not implemented.');
    },
    _onRemoveAllTags: function() {
        alert('Not implemented.');
    },
    _onRemoveTag: function(tagRecord) {
        console.log('Remove tag:', tagRecord.data);
        alert('Not implemented.');
    },
});
