/**
 * Controller for the subject overview.
 */
Ext.define('devilry_subjectadmin.controller.CreateNewPeriod', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'createnewperiod.CreateNewPeriod'
    ],

    requires: [
        'Ext.util.KeyNav',
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    models: ['Subject', 'Period'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }, {
        ref: 'formErrorList',
        selector: 'createnewperiod alertmessagelist#formErrorList'
    }, {
        ref: 'overview',
        selector: 'createnewperiod'
    }, {
        ref: 'header',
        selector: 'createnewperiod #header'
    }, {
        ref: 'shortNameField',
        selector: 'createnewperiod textfield[name=short_name]'
    }, {
        ref: 'formPanel',
        selector: 'createnewperiod form'
    }],

    init: function() {
        this.control({
            'viewport createnewperiod form': {
                render: this._onRender,
            },
            
            'viewport createnewperiod #new_period_start_time': {
                change: this._setMinimumValueOnEndTime
            },

            'viewport createnewperiod #saveButton': {
                click: this._onSave
            },
            'viewport createnewperiod textfield[name=long_name]': {
                render: this._onRenderLongName,
                blur: this._onLongNameBlur
            }
        });
    },

    _setMinimumValueOnEndTime: function(datefield, newFullValue, oldFullValue) {
        endtime = Ext.getCmp("new_period_end_time");
        endtime.setMinimumValue(newFullValue);
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.subject_id = this.getOverview().subject_id;
        this._loadSubject(this.subject_id);
        this.getFormPanel().keyNav = Ext.create('Ext.util.KeyNav', this.getFormPanel().el, {
            enter: this._onSave,
            scope: this
        });
        //this._setInitialValues();
    },

    _loadSubject: function(subject_id) {
        this.getSubjectModel().load(subject_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadSubjectSuccess(record);
                } else {
                    this.onLoadFailure(operation);
                }
            }
        });
    },
    _onLoadSubjectSuccess: function(record) {
        this.subjectRecord = record;
        var title = interpolate(gettext('Create %(period_term)s'), {
            period_term: gettext('period')
        }, true);
        this.application.setTitle(Ext.String.format('{0} - {1}',
            title, this.subjectRecord.get('short_name')));
        this.getHeader().update({
            heading: title,
            subheading: record.get('long_name')
        });
        this.setSubviewBreadcrumb(this.subjectRecord, 'Subject', [], title);
    },

    _onRenderLongName: function(field) {
        Ext.defer(function() {
            // NOTE: Using defer avoids that the text style remains
            // emptyText-gray (I assume it does no because render is fired
            // before the style is applied).
            field.focus();
        }, 100);
    },
    _onLongNameBlur: function(field) {
        var shortnamefield = this.getShortNameField();
        if(shortnamefield.getValue() === '') {
            var value = field.getValue();
            var short_name = devilry_subjectadmin.utils.AutoGenShortname.autogenShortname(value);
            shortnamefield.setValue(short_name);
        }
    },

    _mask: function() {
        this.getOverview().getEl().mask(gettext('Saving') + ' ...');
    },
    _unmask: function() {
        this.getOverview().getEl().unmask();
    },

    _onSave: function() {
        var form = this.getFormPanel().getForm();
        if(form.isValid) {
            var periodRecord = Ext.create('devilry_subjectadmin.model.Period', {
                parentnode: this.subjectRecord.get('id')
            });
            form.updateRecord(periodRecord);
            this._mask();
            this.getPeriodModel().proxy.addListener({ // NOTE: We add the listener only for this save, and remove it again in the callback.
                scope: this,
                exception: this._onProxyError
            });
            periodRecord.save({
                scope: this,
                callback: function(record, operation) {
                    this.getPeriodModel().proxy.removeListener({
                        scope: this,
                        exception: this._onProxyError
                    });
                    if(operation.success) {
                        this._onSuccessfulSave(record);
                    }
                }
            });
        }
    },

    _onSuccessfulSave: function(record) {
        this._unmask();
        this.application.route.navigate(
            devilry_subjectadmin.utils.UrlLookup.periodOverview(record.get('id')));
    },
    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        this.getFormErrorList().removeAll();
        this.handleProxyError(this.getFormErrorList(), this.getFormPanel(),
            response, operation);
    }

    //_setInitialValues: function() {
        //Ext.defer(function() {
            //this.getFormPanel().getForm().setValues({
                //long_name: 'A',
                //short_name: 'a',
                //start_time: new Date(2000, 1, 1),
                //end_time: new Date(2005, 12, 24)
            //});
        //}, 300, this);
    //}
});
