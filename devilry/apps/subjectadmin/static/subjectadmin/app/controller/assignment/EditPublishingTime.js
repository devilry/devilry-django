/**
 * Controller for editing publishing time of an assignment.
 */
Ext.define('subjectadmin.controller.assignment.EditPublishingTime', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.form.ErrorUtils',
        'themebase.RestfulApiProxyErrorHandler'
    ],

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
                render: this._onRenderWindow
            },
            'editpublishingtime savebutton': {
                click: this._onSave
            },
            'editpublishingtime-widget button': {
                click: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getPublishingTimeWidget().enable();
        this._updatePublishingTimeWidget();
    },

    _onRenderWindow: function() {
        this.getPublishingTimeField().setValue(this.assignmentRecord.get('publishing_time'));
    },

    _onSave: function() {
        var form = this.getFormPanel().getForm();
        if(form.isDirty()) {
            var assignmentRecord = this.assignmentRecord;
            form.updateRecord(assignmentRecord);
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
        this._updatePublishingTimeWidget();
    },

    _onSaveFailure: function(record, operation) {
        this._getMaskElement().unmask();
        var errorhandler = Ext.create('themebase.RestfulApiProxyErrorHandler');
        errorhandler.addErrors(operation);
        this.getAlertMessageList().addMany(errorhandler.errormessages, 'error');
        themebase.form.ErrorUtils.addFieldErrorsToAlertMessageList(
            this.getFormPanel(), errorhandler.fielderrors, this.getAlertMessageList()
        );
        themebase.form.ErrorUtils.markFieldErrorsAsInvalid(
            this.getFormPanel(), errorhandler.fielderrors
        );
    },

    _onEdit: function() {
        Ext.widget('editpublishingtime', {
            assignmentRecord: this.assignmentRecord
        }).show();
    },

    _updatePublishingTimeWidget: function() {
        var published = this.assignmentRecord.get('publishing_time') < Ext.Date.now();
        var title, tpl;

        // The fallback is to make it possible to test. We assume that translations is always
        // active in production
        var fallback = Ext.Date.format(this.assignmentRecord.get('publishing_time'), 'Y-m-d H:i');
        fallback += ' ' + (published? 'is published': 'not published');

        if(published) {
            title = dtranslate('subjectadmin.assignment.published.title');
            tpl = dtranslate('subjectadmin.assignment.published.body', fallback);
        } else {
            title = dtranslate('subjectadmin.assignment.notpublished.title');
            tpl = dtranslate('subjectadmin.assignment.notpublished.body', fallback);
        }
        var publishing_time = this.assignmentRecord.get('publishing_time');
        this.getPublishingTimeWidget().updateTitle(title);
        this.getPublishingTimeWidget().updateBody([tpl], {
            publishing_time: Ext.Date.format(publishing_time, dtranslate('Y-m-d H:i'))
        });
    }
});
