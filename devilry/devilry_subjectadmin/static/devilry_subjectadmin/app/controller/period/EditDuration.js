/**
 * Controller for editing start/end time of a period.
 */
Ext.define('devilry_subjectadmin.controller.period.EditDuration', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'period.EditDurationPanel',
        'period.EditDurationWidget'
    ],

    requires: [
        'Ext.util.KeyNav',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    models: ['Period'],
    controllers: [
        'period.Overview'
    ],

    refs: [{
        ref: 'cardContainer',
        selector: 'editperiod_duration-widget'
    }, {
        ref: 'readOnlyView',
        selector: 'editperiod_duration-widget #readDuration'
    }, {
        ref: 'readOnlyViewBody',
        selector: 'editperiod_duration-widget #readDuration markupmoreinfobox'
    }, {

        ref: 'editDuration',
        selector: 'editperiod_duration-widget editperiod_duration'
    }, {
        ref: 'startTimeField',
        selector: 'editperiod_duration-widget editperiod_duration devilry_extjsextras-datetimefield[name=start_time]'
    }, {
        ref: 'endTimeField',
        selector: 'editperiod_duration-widget editperiod_duration devilry_extjsextras-datetimefield[name=end_time]'
    }, {
        ref: 'formPanel',
        selector: 'editperiod_duration-widget editperiod_duration form'
    }, {
        ref: 'alertMessageList',
        selector: 'editperiod_duration-widget editperiod_duration alertmessagelist'
    }],

    init: function() {
        // This is called when the application is initialized, not when the window is opened
        this.application.addListener({
            scope: this,
            periodSuccessfullyLoaded: this._onLoadPeriod
        });
        this.control({
            'editperiod_duration-widget #readDuration': {
                edit: this._onEdit
            },
            'editperiod_duration-widget editperiod_duration form devilry_extjsextras-datetimefield': {
                allRendered: this._onRenderForm
            },
            'editperiod_duration-widget editperiod_duration #okbutton': {
                click: this._onSave
            },
            'editperiod_duration-widget editperiod_duration #cancelbutton': {
                click: this._onCancel
            }
        });
    },

    _onLoadPeriod: function(periodRecord) {
        this.periodRecord = periodRecord;
        this.getReadOnlyView().enable();
        this._updateDurationWidget();
    },
    
    //////////////////////////////////
    //
    // View pubtime
    //
    //////////////////////////////////

    _showReadView: function() {
        this.getCardContainer().getLayout().setActiveItem('readDuration');
    },

    _updateDurationWidget: function() {
        this.getReadOnlyViewBody().update({
            start_time: this.periodRecord.formatStartTime(),
            end_time: this.periodRecord.formatEndTime()
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
        this.getCardContainer().getLayout().setActiveItem('editDuration');
        this.getStartTimeField().setValue(this.periodRecord.get('start_time'));
        this.getEndTimeField().setValue(this.periodRecord.get('end_time'));
        Ext.defer(function() {
            this.getStartTimeField().focus();
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
        var periodRecord = this.periodRecord;
        form.updateRecord(periodRecord);
        this._getMaskElement().mask(gettext('Saving') + ' ...');

        this.getPeriodModel().proxy.addListener({
            scope: this,
            exception: this._onProxyError
        });
        periodRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.getPeriodModel().proxy.removeListener({
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
        this._updateDurationWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        this.getAlertMessageList().removeAll();
        this.handleProxyError(this.getAlertMessageList(), this.getFormPanel(),
            response, operation);
    }
});
