/**
 * Controller for editing the anonymous attribute of an assignment.
 */
Ext.define('devilry_subjectadmin.controller.assignment.EditAnonymous', {
    extend: 'Ext.app.Controller',
    mixins: {
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },

    views: [
        'assignment.EditAnonymous',
        'assignment.EditAnonymousWidget'
    ],

    controllers: [
        'assignment.Overview'
    ],

    models: ['Assignment'],

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
            'editanonymous form checkbox': {
                render: this._onRenderForm
            },
            'editanonymous savebutton': {
                click: this._onSave
            },
            'editanonymous cancelbutton': {
                click: this._close
            },
            'editanonymous-widget': {
                edit: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getAnonymousWidget().enable();
        this._updateAnonymousWidget();
    },

    _onRenderForm: function() {
        this.getAnonymousField().setValue(this.assignmentRecord.get('anonymous'));
        this.getEditAnonymous().mon(this.getAssignmentModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onSave,
            scope: this
        });
        Ext.defer(function() {
            this.getFormPanel().down('checkbox').focus();
        }, 100, this);
    },

    _close: function() {
        this.getEditAnonymous().close();
    },

    _onSave: function() {
        this.getAlertMessageList().removeAll();
        var form = this.getFormPanel().getForm();
        var assignmentRecord = this.assignmentRecord;
        form.updateRecord(assignmentRecord);
        this._getMaskElement().mask(gettext('Saving ...'));
        assignmentRecord.save({
            scope: this,
            success: this._onSaveSuccess
        });
    },

    _getMaskElement: function() {
        return this.getFormPanel().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._close();
        this._updateAnonymousWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        this.handleProxyError(this.getAlertMessageList(), this.getFormPanel(),
            response, operation);
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
            title = gettext('Anonymous');
            body = gettext('Examiners and students can not see each other and they can not communicate.');
        } else {
            title = gettext('Not anonymous');
            body = gettext('Examiners and students can see each other and communicate.');
        }
        var anonymous = this.assignmentRecord.get('anonymous');
        this.getAnonymousWidget().updateTitle(title);
        this.getAnonymousWidget().updateText(body);
    }
});
