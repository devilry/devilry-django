/**
 * Controller for the assignment overview.
 */
Ext.define('subjectadmin.controller.assignment.Overview', {
    extend: 'Ext.app.Controller',

    //requires: [
    //],
    views: [
        'assignment.Overview',
        'ActionList',
        'assignment.EditPublishingTime',
        'assignment.EditPublishingTimeWidget'
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
        ref: 'publishingTimeWidget',
        selector: 'editpublishingtime-widget'
    }, {
        ref: 'primaryTitle',
        selector: 'centertitle[itemId=primaryTitle]'
    }, {
        ref: 'assignmentOverview',
        selector: 'assignmentoverview'
    }],

    init: function() {
        this.control({
            'viewport assignmentoverview': {
                render: this._onAssignmentViewRender
            },
            'viewport assignmentoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport assignmentoverview editpublishingtime-widget button': {
                click: this._onEditPublishingTime
            }
        });
    },

    _onAssignmentViewRender: function() {
        this.subject_shortname = this.getAssignmentOverview().subject_shortname;
        this.period_shortname = this.getAssignmentOverview().period_shortname;
        this.assignment_shortname = this.getAssignmentOverview().assignment_shortname;
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
            this.getAssignmentOverview().getEl().mask(tpl.apply({
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
        this.getPublishingTimeWidget().updateTitle(title);
        this.getPublishingTimeWidget().updateBody([tpl], {
            publishing_time: Ext.Date.format(publishing_time, dtranslate('Y-m-d H:i'))
        });
    },

    _onEditGradeEditor: function() {
        console.log('grade', this.getGradeEditorSidebarBox());
    },

    _onEditPublishingTime: function() {
        Ext.widget('editpublishingtime', {
            assignmentRecord: this.assignmentRecord
        }).show();
    }
});
