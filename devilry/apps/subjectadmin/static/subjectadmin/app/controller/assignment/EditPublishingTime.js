/**
 * Controller for editing publishing time of an assignment.
 */
Ext.define('subjectadmin.controller.assignment.EditPublishingTime', {
    extend: 'Ext.app.Controller',

    views: [
        'assignment.EditPublishingTime'
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
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.control({
            'editpublishingtime': {
                render: this._onRender
            },
            'editpublishingtime savebutton': {
                click: this._onSave
            }
        });
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
    }
});
