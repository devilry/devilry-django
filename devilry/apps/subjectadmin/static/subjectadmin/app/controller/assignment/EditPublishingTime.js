/**
 * Controller for editing publishing time of an assignment.
 */
Ext.define('subjectadmin.controller.assignment.EditPublishingTime', {
    extend: 'Ext.app.Controller',

    views: [
        'assignment.EditPublishingTime',
        'assignment.EditPublishingTimeWidget'
    ],

    controllers: [
        'assignment.Overview'
    ],

    refs: [{
        ref: 'editPublishingTime',
        selector: 'editpublishingtime'
    }, {
        ref: 'publishingTimeField',
        selector: 'editpublishingtime themebase-datetimefield'
    }, {
        ref: 'formPanel',
        selector: 'editpublishingtime form'
    }, {
        ref: 'alertMessageList',
        selector: 'editpublishingtime alertmessagelist'
    }, {
        ref: 'publishingTimeWidget',
        selector: 'editpublishingtime-widget'
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'editpublishingtime': {
                render: this._onRender
            },
            'editpublishingtime savebutton': {
                click: this._onSave
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this._updatePublishingTimeBox();
    },

    _getAssignmentRecord: function() {
        return this.getEditPublishingTime().assignmentRecord;
    },

    /** When the window has been successfully rendered */
    _onRender: function() {
        this.getPublishingTimeField().setValue(this._getAssignmentRecord().get('publishing_time'));
    },

    _onSave: function() {
        var form = this.getFormPanel().getForm();
        if(form.isDirty()) {
            var assignmentRecord = this._getAssignmentRecord();
            form.updateRecord(assignmentRecord);
            console.log(assignmentRecord.get('publishing_time').toString());
            this._getMaskElement().mask(dtranslate('themebase.saving'));
            assignmentRecord.save({
                scope: this,
                success: this._onSaveSuccess,
                failure: this._onSaveFailure
            });
        } else {
            this.close();
        }
    },

    _getMaskElement: function() {
        return this.getFormPanel().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this.getEditPublishingTime().close();
    },

    _onSaveFailure: function(record, operation) {
        this._getMaskElement().unmask();
        themebase.form.ErrorUtils.handleRestErrorsInForm(
            operation, this.getFormPanel(), this.getAlertMessageList()
        );
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
});
