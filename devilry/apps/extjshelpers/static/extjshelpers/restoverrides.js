/* Override the method that is used to submit forms. */
Ext.override(Ext.form.action.Submit, {
    run: function() {
        var record = this.form.getRecord();
        if(record) { // Update the current record with data from form if editing existing (previously loaded with loadRecord())
            this.form.updateRecord(record);
        } else { // Create new record
            record = Ext.ModelManager.create(this.form.getValues(), this.form.model);
        }

        // save() automatically uses the correct REST method (post for create and put for update).
        record = record.save({
            form: this.form,
            success: this.onSuccess,
            failure: this.onFailure,
            scope: this,
            timeout: (this.timeout * 1000) || (this.form.timeout * 1000),
        });

        this.form.reset();
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
        this.form.markInvalid(operation.responseData.errors);

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
