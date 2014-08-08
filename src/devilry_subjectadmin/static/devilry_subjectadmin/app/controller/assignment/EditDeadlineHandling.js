/**
 * Controller for editing the deadline_handling attribute of an assignment.
 */
Ext.define('devilry_subjectadmin.controller.assignment.EditDeadlineHandling', {
    extend: 'Ext.app.Controller',
    mixins: {
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },
    
    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    views: [
        'assignment.EditDeadlineHandlingPanel',
        'assignment.EditDeadlineHandlingWidget'
    ],

    controllers: [
        'assignment.Overview'
    ],

    models: ['Assignment'],

    refs: [{
        ref: 'cardContainer',
        selector: 'editdeadline_handling-widget'
    }, {
        ref: 'readOnlyView',
        selector: 'editdeadline_handling-widget #readDeadlineHandling'
    }, {
        ref: 'readOnlyViewBody',
        selector: 'editdeadline_handling-widget #readDeadlineHandling markupmoreinfobox'

    }, {
        ref: 'editDeadlineHandling',
        selector: 'editdeadline_handling-widget editdeadline_handlingpanel'
    }, {
        ref: 'deadlineHandlingField',
        selector: 'editdeadline_handling-widget editdeadline_handlingpanel checkbox'
    }, {
        ref: 'formPanel',
        selector: 'editdeadline_handling-widget editdeadline_handlingpanel form'
    }, {
        ref: 'alertMessageList',
        selector: 'editdeadline_handling-widget editdeadline_handlingpanel alertmessagelist'
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'editdeadline_handling-widget #readDeadlineHandling': {
                edit: this._onEdit
            },
            'editdeadline_handling-widget editdeadline_handlingpanel form checkbox': {
                render: this._onRenderForm
            },
            'editdeadline_handling-widget editdeadline_handlingpanel #okbutton': {
                click: this._onSave
            },
            'editdeadline_handling-widget editdeadline_handlingpanel #cancelbutton': {
                click: this._onCancel
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getReadOnlyView().enable();
        this._updateDeadlineHandlingWidget();
    },


    //////////////////////////////////
    //
    // The current stored value view
    //
    //////////////////////////////////
    
    _showReadView: function() {
        this.getCardContainer().getLayout().setActiveItem('readDeadlineHandling');
    },

    _updateDeadlineHandlingWidget: function() {
        var deadline_handling = this.assignmentRecord.get('deadline_handling');
        var SOFT = 0;
        var HARD = 1;
        this.getReadOnlyViewBody().update({
            deadline_handling: deadline_handling,
            SOFT: SOFT,
            HARD: HARD
        });
    },

    _onEdit: function() {
        this._showEditView();
    },


    //////////////////////////////////
    //
    // Edit deadline_handling
    //
    //////////////////////////////////
    _showEditView: function() {
        // this.getCardContainer().getLayout().setActiveItem('editDeadlineHandling');
        // this.getDeadlineHandlingField().setValue(this.assignmentRecord.get('deadline_handling'));
        // Ext.defer(function() {
        //     this.getFormPanel().down('checkbox').focus();
        // }, 100, this);
        window.location.href = devilry_subjectadmin.utils.UrlLookup.updateAssignment(this.assignmentRecord.get('id'));
    },

    _onRenderForm: function() {
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onSave,
            scope: this
        });
    },

    _onCancel: function() {
        this._showReadView();
    },

    _onSave: function() {
        this.getAlertMessageList().removeAll();
        var form = this.getFormPanel().getForm();
        var assignmentRecord = this.assignmentRecord;
        var deadline_handling = form.getValues().deadline_handling;
        assignmentRecord.set('deadline_handling', deadline_handling);
        this._getMaskElement().mask(gettext('Saving') + ' ...');

        this.getAssignmentModel().proxy.addListener({
            scope: this,
            exception: this._onProxyError
        });
        assignmentRecord.save({
            scope: this,
            success: this._onSaveSuccess,
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

    _getMaskElement: function() {
        return this.getFormPanel().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._showReadView();
        this._updateDeadlineHandlingWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        this.getAlertMessageList().removeAll();
        this.handleProxyError(this.getAlertMessageList(), this.getFormPanel(),
        response, operation);
    }
});
