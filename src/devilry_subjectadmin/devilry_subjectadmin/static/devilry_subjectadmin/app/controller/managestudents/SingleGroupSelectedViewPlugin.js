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

    _createStudentsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getCandidateModel(),
            data: this.groupRecord.get('students')
        });
        return store;
    },
    _onRemoveStudent: function(candidateRecord) {
        Ext.MessageBox.alert('Not implemented', 'See <a href="https://github.com/devilry/devilry-django/issues/215" target="_blank">issue 215</a> for info about how this will work.');
        //console.log('Remove student:', candidateRecord.data);
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
        //console.log('Remove examiner:', examinerRecord.data);
        alert('Not implemented.');
    },

    _createTagsStore: function() {
        //console.log(this.groupRecord.data);
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
        var tags = this.groupRecord.get('tags');
        Ext.Array.each(tags, function(tagObj, index) {
            if(tagObj.tag == tagRecord.get('tag')) {
                Ext.Array.erase(tags, index, 1);
                return false; // break
            }
        }, this);
        console.log(this.groupRecord.get('tags'));
        this.groupRecord.save();
    },
});
