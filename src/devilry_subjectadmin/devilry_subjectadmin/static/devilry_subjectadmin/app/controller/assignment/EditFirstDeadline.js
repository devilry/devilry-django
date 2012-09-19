/**
 * Controller for editing first deadline of an assignment.
 */
Ext.define('devilry_subjectadmin.controller.assignment.EditFirstDeadline', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'assignment.EditFirstDeadlinePanel',
        'assignment.EditFirstDeadlineWidget'
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
        ref: 'cardContainer',
        selector: 'editfirstdeadline-widget'
    }, {
        ref: 'readOnlyView',
        selector: 'editfirstdeadline-widget #readFirstDeadline'
    }, {
        ref: 'readOnlyViewBody',
        selector: 'editfirstdeadline-widget #readFirstDeadline markupmoreinfobox'
    }, {

        ref: 'editFirstDeadline',
        selector: 'editfirstdeadline-widget editfirstdeadlinepanel'
    }, {
        ref: 'firstDeadlineField',
        selector: 'editfirstdeadline-widget editfirstdeadlinepanel devilry_extjsextras-datetimefield'
    }, {
        ref: 'formPanel',
        selector: 'editfirstdeadline-widget editfirstdeadlinepanel form'
    }, {
        ref: 'alertMessageList',
        selector: 'editfirstdeadline-widget editfirstdeadlinepanel alertmessagelist'
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'editfirstdeadline-widget #readFirstDeadline': {
                edit: this._onEdit
            },
            'editfirstdeadline-widget editfirstdeadlinepanel form devilry_extjsextras-datetimefield': {
                allRendered: this._onRenderForm
            },
            'editfirstdeadline-widget editfirstdeadlinepanel #okbutton': {
                click: this._onSave
            },
            'editfirstdeadline-widget editfirstdeadlinepanel #cancelbutton': {
                click: this._onCancel
            },
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getReadOnlyView().enable();
        this._updateFirstDeadlineWidget();
    },
    
    //////////////////////////////////
    //
    // View pubtime
    //
    //////////////////////////////////

    _showReadView: function() {
        this.getCardContainer().getLayout().setActiveItem('readFirstDeadline');
    },

    _updateFirstDeadlineWidget: function() {
        this.getReadOnlyViewBody().update({
            first_deadline: this.assignmentRecord.formatFirstDeadline()
        });
    },

    _onEdit: function() {
        this._showEditView();
    },

    
    //////////////////////////////////
    //
    // Edit pubtime
    //
    //////////////////////////////////

    _showEditView: function() {
        this.getCardContainer().getLayout().setActiveItem('editFirstDeadline');
        this.getFirstDeadlineField().setValue(this.assignmentRecord.get('first_deadline'));
        Ext.defer(function() {
            this.getFormPanel().down('devilry_extjsextras-datetimefield').focus();
        }, 200, this);
    },

    _onRenderForm: function() {
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onSave,
            scope: this
        });
    },

    _onSave: function() {
        var form = this.getFormPanel().getForm();
        var assignmentRecord = this.assignmentRecord;
        form.updateRecord(assignmentRecord);
        this._getMaskElement().mask(gettext('Saving ...'));

        this.getAssignmentModel().proxy.addListener({
            scope: this,
            exception: this._onProxyError
        });
        assignmentRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.getAssignmentModel().proxy.removeListener({
                    scope: this,
                    exception: this._onProxyError
                });
                if(operation.success) {
                    this._onSaveSuccess();
                }
            }
        });
    },

    _onCancel: function() {
        this._showReadView();
    },

    _getMaskElement: function() {
        return this.getFormPanel().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._showReadView();
        this._updateFirstDeadlineWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        this.getAlertMessageList().removeAll();
        this.handleProxyError(this.getAlertMessageList(), this.getFormPanel(),
            response, operation);
    }
});
