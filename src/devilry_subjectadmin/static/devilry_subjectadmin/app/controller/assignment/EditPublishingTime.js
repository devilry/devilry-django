/**
 * Controller for editing publishing time of an assignment.
 */
Ext.define('devilry_subjectadmin.controller.assignment.EditPublishingTime', {
    extend: 'Ext.app.Controller',
    mixins: {
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },
    
    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    views: [
        'assignment.EditPublishingTimePanel',
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
        ref: 'cardContainer',
        selector: 'editpublishingtime-widget'
    }, {
        ref: 'readOnlyView',
        selector: 'editpublishingtime-widget containerwithedittitle#readPublishingTime'
    }, {
        ref: 'readOnlyViewBody',
        selector: 'editpublishingtime-widget markupmoreinfobox'
    }, {

        ref: 'editPublishingTime',
        selector: 'editpublishingtime-widget editpublishingtimepanel'
    }, {
        ref: 'publishingTimeField',
        selector: 'editpublishingtime-widget editpublishingtimepanel devilry_extjsextras-datetimefield'
    }, {
        ref: 'formPanel',
        selector: 'editpublishingtime-widget editpublishingtimepanel form'
    }, {
        ref: 'alertMessageList',
        selector: 'editpublishingtime-widget editpublishingtimepanel alertmessagelist'
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'editpublishingtime-widget #readPublishingTime': {
                edit: this._onEdit
            },
            'editpublishingtime-widget editpublishingtimepanel form devilry_extjsextras-datetimefield': {
                allRendered: this._onRenderForm
            },
            'editpublishingtime-widget editpublishingtimepanel #okbutton': {
                click: this._onSave
            },
            'editpublishingtime-widget editpublishingtimepanel #cancelbutton': {
                click: this._onCancel
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getReadOnlyView().enable();
        this._updatePublishingTimeWidget();
    },
    
    //////////////////////////////////
    //
    // View pubtime
    //
    //////////////////////////////////

    _showReadView: function() {
        this.getCardContainer().getLayout().setActiveItem('readPublishingTime');
    },

    _updatePublishingTimeWidget: function() {
        var offset_from_now = this.assignmentRecord.formatPublishOffsetFromNow();
        var is_published = this.assignmentRecord.get('is_published');
        this.getReadOnlyView().updateTitle(gettext('Publishing time'));
        this.getReadOnlyViewBody().update({
            publishing_time: this.assignmentRecord.formatPublishingTime(),
            offset_from_now: offset_from_now,
            is_published: is_published
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
        // this.getCardContainer().getLayout().setActiveItem('editPublishingTime');
        // this.getPublishingTimeField().setValue(this.assignmentRecord.get('publishing_time'));
        // Ext.defer(function() {
        //     this.getFormPanel().down('devilry_extjsextras-datetimefield').focus();
        // }, 200, this);
        window.location.href = devilry_subjectadmin.utils.UrlLookup.updateAssignment(this.assignmentRecord.get('id'));
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
        this._getMaskElement().mask(gettext('Saving') + ' ...');

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
        this._updatePublishingTimeWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        this.getAlertMessageList().removeAll();
        this.handleProxyError(this.getAlertMessageList(), this.getFormPanel(),
            response, operation);
    }
});
