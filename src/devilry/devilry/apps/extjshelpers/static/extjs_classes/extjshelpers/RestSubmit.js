/**
 * Restful submit with support for HTTP error codes and PUT, POST, DELETE and
 * GET. This is achieved in cooperation with {@link devilry.extjshelpers.RestProxy}.
 *
 * # Usage
 *
 *      myform.getForm().doAction('devilryrestsubmit', {...});
 * 
 * instead of
 *
 *      myform.getForm().submit({...});
 * 
 * Just remember require this class with:
 *
 *      requires: ['devilry.extjshelpers.RestSubmit']
 *
 * or
 *
 *      Ext.require('devilry.extjshelpers.RestSubmit');
 *
 * # See also
 * {@link devilry.extjshelpers.RestProxy}.
 * */
Ext.define('devilry.extjshelpers.RestSubmit', {
    extend: 'Ext.form.action.Submit',
    alias: 'formaction.devilryrestsubmit',

    run: function() {
        var record = this.form.getRecord();
        if(this.method == "DELETE") {
            this.deleteRequest(record);
        } else {
            this.saveRequest(record);
        }
    },

    deleteRequest: function(record) {
        if(!record) {
            throw "Can not DELETE a non-existing record.";
        }
        record = record.destroy({
            form: this.form,
            success: this.onSuccess,
            failure: this.onFailure,
            scope: this,
            timeout: (this.timeout * 1000) || (this.form.timeout * 1000),
        });
    },

    saveRequest: function(record) {
        if(record) { // Update the current record with data from form if editing existing (previously loaded with loadRecord())
            this.form.updateRecord(record);
        } else { // Create new record
            record = Ext.ModelManager.create(this.form.getValues(), this.model);
        }

        // save() automatically uses the correct REST method (post for create and put for update).
        record = record.save({
            form: this.form,
            success: this.onSuccess,
            failure: this.onFailure,
            scope: this,
            timeout: (this.timeout * 1000) || (this.form.timeout * 1000),
        });
    },


    onSuccess: function(record, operation) {
        this.record = record;
        this.operation = operation;
        this.form.afterAction(this, true);
    },

    onFailure: function(record, operation){
        this.record = record; // Always null?
        this.operation = operation;
        this.response = operation.response;
        if(operation.responseData) {
            this.form.markInvalid(operation.responseData.items.fielderrors);
        }

        if(operation.error.status === 0) {
            this.failureType = Ext.form.action.Action.CONNECT_FAILURE;
        } else if(operation.error.status >= 400 && operation.error.status < 500) {
            this.failureType = Ext.form.action.Action.SERVER_INVALID;
        } else {
            this.failureType = Ext.form.action.Action.LOAD_FAILURE;
        }
        this.form.afterAction(this, false);
    }
});
