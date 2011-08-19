/** Apanel for editing RestfulSimplified models. */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditPanel', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditPanelBase',
    alias: 'widget.restfulsimplified_editpanel',
    requires: ['devilry.extjshelpers.RestSubmit'],

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    onSave: function() {
        this.errorlist.clearErrors();
        this.beforeSave();
    },

    beforeSave: function() {
        this.doSave();
    },

    doSave: function() {
        var me = this;
        this.editform.getForm().doAction('devilryrestsubmit', {
            submitEmptyText: true,
            waitMsg: 'Saving item...',
            model: this.model,
            success: function(form, action) {
                me.onSaveSuccess(form, action);
            },
            failure: function(form, action) {
                me.onSaveFailure(form, action);
            }
        });
    },

    onSaveSuccess: function(form, action) {
        var record = action.record;        
        this.fireEvent('saveSucess', record);
    },

    onSaveFailure: function(record, action) {
        var errormessages = action.operation.responseData.items.errormessages;
        var me = this;
        Ext.each(errormessages, function(errormessage) {
            me.errorlist.addError(errormessage);
        });
    }
});
