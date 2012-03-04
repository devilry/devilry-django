/**
 * Controller for editing the anonymous attribute of an assignment.
 */
Ext.define('subjectadmin.controller.assignment.EditAnonymous', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.form.ErrorUtils',
        'themebase.RestfulApiProxyErrorHandler'
    ],

    views: [
        'assignment.EditAnonymous',
        'assignment.EditAnonymousWidget'
    ],

    controllers: [
        'assignment.Overview'
    ],

    refs: [{
        ref: 'editAnonymous',
        selector: 'editanonymous'
    }, {
        ref: 'anonymousField',
        selector: 'editanonymous checkbox'
    }, {
        ref: 'formPanel',
        selector: 'editanonymous form'
    }, {
        ref: 'alertMessageList',
        selector: 'editanonymous alertmessagelist'
    }, {
        ref: 'anonymousWidget',
        selector: 'editanonymous-widget'
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'editanonymous': {
                render: this._onRenderWindow
            },
            'editanonymous savebutton': {
                click: this._onSave
            },
            'editanonymous cancelbutton': {
                click: this._close
            },
            'editanonymous-widget button': {
                click: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getAnonymousWidget().enable();
        this._updateAnonymousWidget();
    },

    _onRenderWindow: function() {
        this.getAnonymousField().setValue(this.assignmentRecord.get('anonymous'));
    },

    _close: function() {
        this.getEditAnonymous().close();
    },

    _onSave: function() {
        var form = this.getFormPanel().getForm();
        var oldValue = this.assignmentRecord.get('anonymous');
        var newValue = form.getValues().anonymous;
        if(oldValue != newValue) {
            var assignmentRecord = this.assignmentRecord;
            form.updateRecord(assignmentRecord);
            this._getMaskElement().mask(dtranslate('themebase.saving'));
            assignmentRecord.save({
                scope: this,
                success: this._onSaveSuccess,
                failure: this._onSaveFailure
            });
        } else {
            this._close();
        }
    },

    _getMaskElement: function() {
        return this.getFormPanel().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._close();
        this._updateAnonymousWidget();
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
        Ext.widget('editanonymous', {
            assignmentRecord: this.assignmentRecord
        }).show();
    },

    _updateAnonymousWidget: function() {
        var anonymous = this.assignmentRecord.get('anonymous');
        var title, body;

        if(anonymous) {
            title = dtranslate('subjectadmin.assignment.is_anonymous.title');
            body = dtranslate('subjectadmin.assignment.is_anonymous.body');
        } else {
            title = dtranslate('subjectadmin.assignment.not_anonymous.title');
            body = dtranslate('subjectadmin.assignment.not_anonymous.body');
        }
        var anonymous = this.assignmentRecord.get('anonymous');
        this.getAnonymousWidget().updateTitle(title);
        this.getAnonymousWidget().updateBody(body);
    }
});
