/**
 * Controller for the assignment overview.
 */
Ext.define('subjectadmin.controller.assignment.Overview', {
    extend: 'Ext.app.Controller',

    //requires: [
    //],
    views: [
        'assignment.Assignment',
        'ActionList',
        'assignment.EditPublishingTime'
    ],

    stores: [
        'SingleAssignment'
    ],

    controllers: [
        'assignment.EditPublishingTime'
    ],

    refs: [{
        ref: 'gradeEditorSidebarBox',
        selector: 'editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'publishingTimeSidebarBox',
        selector: 'editablesidebarbox[itemId=publishingtime]'
    }, {
        ref: 'primaryTitle',
        selector: 'centertitle[itemId=primaryTitle]'
    }, {
        ref: 'assignmentView',
        selector: 'assignment'
    }],

    init: function() {
        this.control({
            'viewport assignment': {
                render: this._onAssignmentViewRender
            },
            'viewport assignment editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport assignment editablesidebarbox[itemId=publishingtime] button': {
                click: this._onEditPublishingTime
            },
            'viewport assignment editablesidebarbox[itemId=publishingtime] button': {
                click: this._onEditPublishingTime
            },
        });
    },

    _onAssignmentViewRender: function() {
        this.subject_shortname = this.getAssignmentView().subject_shortname;
        this.period_shortname = this.getAssignmentView().period_shortname;
        this.assignment_shortname = this.getAssignmentView().assignment_shortname;
        this._loadAssignment();
    },

    _loadAssignment: function() {
        var store = this.getSingleAssignmentStore();
        store.loadAssignment(
            this.subject_shortname, this.period_shortname, this.assignment_shortname,
            this._onLoadAssignment, this
        );
    },

    _onLoadAssignment: function(records, operation) {
        if(operation.success) {
            this._onLoadAssignmentSuccess(records[0]);
        } else {
            this._onLoadAssignmentFailure(operation);
        }
    },

    _onLoadAssignmentFailure: function(operation) {
        var tpl = Ext.create('Ext.XTemplate',
            '<h2>{title}</h2>',
            '<p>{subject_shortname}.{period_shortname}.{assignment_shortname}</p>'
        );
        Ext.defer(function() { // NOTE: The delay is required for the mask to draw itself correctly.
            this.getAssignmentView().getEl().mask(tpl.apply({
                title: dtranslate('themebase.doesnotexist'),
                subject_shortname: this.subject_shortname,
                period_shortname: this.period_shortname,
                assignment_shortname: this.assignment_shortname
            }), 'messagemask');
        }, 50, this);
    },

    _onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.getPrimaryTitle().update(record.get('long_name'));
        this._updatePublishingTimeBox();
    },

    _updatePublishingTimeBox: function() {
        var published = this.assignmentRecord.get('publishing_time') < Ext.Date.now();
        var title, tpl;
        if(published) {
            title = dtranslate('subjectadmin.assignment.published.title');
            tpl = dtranslate('subjectadmin.assignment.published.body');
        } else {
            title = dtranslate('subjectadmin.assignment.notpublished.title');
            tpl = dtranslate('subjectadmin.assignment.notpublished.body');
        }
        var publishing_time = this.assignmentRecord.get('publishing_time');
        this.getPublishingTimeSidebarBox().updateTitle(title);
        this.getPublishingTimeSidebarBox().updateBody([tpl], {
            publishing_time: Ext.Date.format(publishing_time, dtranslate('Y-m-d H:i'))
        });
    },

    _onEditGradeEditor: function() {
        console.log('grade', this.getGradeEditorSidebarBox());
    },

    _onEditPublishingTime: function() {
        //console.log('pub', this.getPublishingTimeSidebarBox());
        Ext.widget('editpublishingtime', {
            assignmentRecord: this.assignmentRecord
        }).show();
    }
});
