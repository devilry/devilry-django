/** Singleton class with methods for form error parsing. No state is stored in
 * the singleton. */
Ext.define('themebase.form.ErrorUtils', {
    singleton: true,

    /**
     * Get errors from an ``Ext.data.Operation`` object.
     *
     * The returned object guaranteed to have the following attributes:
     *
     *  - **global**: Array of global errors.
     *  - **field**: Map of field errors with field name as key. The __all__
     *    key is removed, since devilry.restful adds this value to global
     *    as well.
     *
     *  @return an object as described above.
     */
    getErrorsFromOperation: function(operation) {
        var restfulErrors = this.getRestErrorsFromOperation(operation);
        if(restfulErrors) {
            return restfulErrors;
        } else {
            return {
                global: this.getErrorMessageFromOperation(operation),
                field: []
            };
        } 
    },

    /** Makes the errors messages contained in the ``responseData`` added to
     * ``Ext.data.Operation`` objects by
     * ``devilry.extjshelpers.RestProxy.setException``.
     *
     * The returned object guaranteed to have the following attributes (unless it is null):
     *
     *  - **global**: Array of global errors.
     *  - **field**: Object of field errors with field name as key. The __all__
     *    key is removed, since devilry.restful adds this value to global
     *    as well.
     *
     *  @return an object as described above, or null if no REST errormessages
     *  can be found in the operation object.
     */
    getRestErrorsFromOperation: function(operation) {
        if(operation.responseData && operation.responseData.items.errormessages) {
            var errors = operation.responseData.items;
            var fielderrors = {};
            if(errors.fielderrors) {
                Ext.Object.each(errors.fielderrors, function(key, value) {
                    if(key != '__all__') {
                        fielderrors[key] = value;
                    }
                });
            }
            return {
                global: errors.errormessages,
                field: fielderrors
            };
        } else {
            return null;
        }
    },

    /** Formats the error object returned by ``Ext.data.Operation.getError(). as
     * a string that can be displayed to users.
     * 
     * @return The formatted string.
     * */
    getErrorMessageFromOperation: function(operation) {
        var error = operation.getError();
        var message;
        if(error.status === 0) {
            message = dtranslate('themebase.lostserverconnection');
        } else {
            message = Ext.String.format('{0}: {1}', error.status, error.statusText);
        }
        return message;
    },

    /**
     * Mark all fields that are both in ``formpanel`` and ``fielderrors`` with
     * using ``field.markInvalid(fielderrors[fieldname])``.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestErrorsFromOperation``.
     * */
    applyFieldErrorsToForm: function(formpanel, fielderrors) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var fieldComponentQuery = Ext.String.format('field[name={0}]', fieldname);
            var match = formpanel.query(fieldComponentQuery);
            if(match.length > 0) {
                var field = match[0];
                field.markInvalid(fielderrors);
            }
        });
    },

    /** Handle errors from an update, create or delete using a model that uses
     * ``devilry.extjshelpers.RestProxy``.
     *
     * @param operation ``Ext.data.Operation`` object.
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param alertmessagelist A ``themebase.AlertMessageList`` object.
     * */
    handleRestErrorsInForm: function(operation, formpanel, alertmessagelist) {
        var errors = this.getErrorsFromOperation(operation);
        alertmessagelist.addMany(errors.global, 'error');
        this.applyFieldErrorsToForm(formpanel, errors.field);
        console.log(errors);
        if(Ext.Object.getSize(errors.field) > 0) {
            alertmessagelist.add({
                message: dtranslate('themebase.form.hasfieldswitherrors'),
                type: 'error'
            });
        }
    }
});
