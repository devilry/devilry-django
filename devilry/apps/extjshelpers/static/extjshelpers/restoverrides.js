/* Override the method that is used to submit forms. We use Ext.data.proxy.Rest
 * for everything, so we have broken submit for other proxies here. */
Ext.override(Ext.form.action.Submit, {
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
            this.form.markInvalid(operation.responseData.errors);
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



/* Since ExtJS for some reason goes into panic mode for any HTTP status
 * code except 200 (and ignores the response text), we need to override
 * setException in the REST proxy and manually decode the responseText.
 * (http://www.sencha.com/forum/showthread.php?135143-RESTful-Model-How-to-indicate-that-the-PUT-operation-failed&highlight=store+failure)
 *
 * However how do we get this into the form when we do not have any link to the form?
 *      - We add the response and the the decoded responsedata to the
 *        operation object, which is available to onFailure in Submit.
 * */
Ext.override(Ext.data.proxy.Rest, {
    setException: function(operation, response){
        operation.response = response;
        operation.responseText = response.responseText;
        try {
            operation.responseData = Ext.JSON.decode(operation.responseText); // May want to use a Reader
        } catch(e) {
            // No operation.responseData if it can not be decoded as JSON.
        }
        operation.setException({
            status: response.status,
            statusText: response.statusText
        });
    }
})
