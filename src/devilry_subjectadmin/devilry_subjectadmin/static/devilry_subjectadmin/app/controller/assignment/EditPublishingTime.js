/**
 * Controller for editing publishing time of an assignment.
 */
Ext.define('devilry_subjectadmin.controller.assignment.EditPublishingTime', {
    extend: 'Ext.app.Controller',
    mixins: {
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },

    views: [
        'assignment.EditPublishingTime',
        'assignment.EditPublishingTimeWidget'
    ],

    requires: [
        'Ext.util.KeyNav',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    models: ['Assignment'],
    controllers: [
        'assignment.Overview'
    ],

    refs: [{
        ref: 'editPublishingTime',
        selector: 'editpublishingtime'
    }, {
        ref: 'publishingTimeField',
        selector: 'editpublishingtime devilry_extjsextras-datetimefield'
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
            'editpublishingtime form devilry_extjsextras-datetimefield': {
                allRendered: this._onRenderForm
            },
            'editpublishingtime savebutton': {
                click: this._onSave
            },
            'editpublishingtime cancelbutton': {
                click: this._close
            },
            'editpublishingtime-widget': {
                edit: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getPublishingTimeWidget().enable();
        this._updatePublishingTimeWidget();
    },

    _onRenderForm: function() {
        this.getPublishingTimeField().setValue(this.assignmentRecord.get('publishing_time'));
        this.getEditPublishingTime().mon(this.getAssignmentModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onSave,
            scope: this
        });
        Ext.defer(function() {
            this.getFormPanel().down('devilry_extjsextras-datetimefield').focus();
        }, 200, this);
    },

    _onSave: function() {
        var form = this.getFormPanel().getForm();
        var assignmentRecord = this.assignmentRecord;
        form.updateRecord(assignmentRecord);
        this._getMaskElement().mask(gettext('Saving ...'));
        assignmentRecord.save({
            scope: this,
            success: this._onSaveSuccess
        });
    },

    _close: function() {
        this.getEditPublishingTime().close();
    },

    _getMaskElement: function() {
        return this.getFormPanel().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._close();
        this._updatePublishingTimeWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        this.handleProxyError(this.getAlertMessageList(), this.getFormPanel,
            response, operation);
    },

    _onEdit: function() {
        Ext.widget('editpublishingtime', {
            assignmentRecord: this.assignmentRecord
        }).show();
    },

    _updatePublishingTimeWidget: function() {
        var offset_from_now = this.assignmentRecord.formatPublishOffsetFromNow();
        var is_published = this.assignmentRecord.get('is_published');
        this.getPublishingTimeWidget().updateTitle(gettext('Publishing time'));
        this.getPublishingTimeWidget().updateBody({
            publishing_time: this.assignmentRecord.formatPublishingTime(),
            offset_from_now: offset_from_now,
            is_published: is_published
        });
    }
});
