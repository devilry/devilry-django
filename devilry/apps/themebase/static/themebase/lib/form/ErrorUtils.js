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
        var restfulErrors = this.getRestfulErrorsFromOperation(operation);
        if(restfulErrors) {
            return restfulErrors;
        } else {
            var restErrors = this.getRestErrorsFromOperation(operation);
            if(restErrors) {
                return restErrors;
            } else {
                return {
                    global: this.getErrorMessageFromOperation(operation),
                    field: []
                };
            }
        } 
    },

    _decodeResponseTextJSON: function(operation) {
        try {
            return Ext.JSON.decode(operation.responseText);
        } catch(e) {
            return null;
        }
    },

    _parseRestAndRestfulErrors: function(errors) {
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
    },

    /** Gets the JSON encoded errors messages contained in
     * ``operation.responseText``. Requires the JSON data
     * to be an object with a list of errors in its ``errormessages`` attribute.
     * The object may also contain a ``fielderrors`` attribute, which should be
     * an object where each attribute is a fieldname with a corresponding list
     * of error messages.
     *
     * This is ment to parse error messages from the python function
     * ``devilry.rest.errorhandlers.create_errordict``.
     *
     * The returned object guaranteed to have the following attributes (unless it is null):
     *
     *  - **global**: Array of global errors.
     *  - **field**: Object of field errors with field name as key. The __all__
     *    key is removed, since these are Django globale global errors which
     *    should be in ``errormessages``.
     *
     *  @return an object as described above, or null if no REST errormessages
     *  can be found in the operation object.
     */
    getRestErrorsFromOperation: function(operation) {
        var responseData = this._decodeResponseTextJSON(operation);
        if(responseData) {
            return this._parseRestAndRestfulErrors(responseData);
        } else {
            return null;
        }
    },

    /** Gets the errors messages contained in the ``responseData`` added to
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
    getRestfulErrorsFromOperation: function(operation) {
        if(operation.responseData && operation.responseData.items) {
            var errors = operation.responseData.items;
            return this._parseRestAndRestfulErrors(errors);
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
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
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

    /**
     * Add field errors to ``AlertMessageList``.
     *
     * Locates form field labels using the key in fielderrors, and prefixes all
     * error messages with the field label.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
     * @param alertmessagelist A ``themebase.AlertMessageList`` object.
     * */
    addFieldErrorsToAlertMessageList: function(formpanel, fielderrors, alertmessagelist) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var fieldComponentQuery = Ext.String.format('field[name={0}]', fieldname);
            var match = formpanel.query(fieldComponentQuery);
            var fielderror = fielderrors.join('. ');
            if(match.length > 0) {
                var field = match[0];
                var message = Ext.String.format('<strong>{0}:</strong> {1}', field.fieldLabel, fielderror)
                alertmessagelist.add({
                    message: message,
                    type: 'error'
                });
            } else {
                throw Ext.String.format(
                    "Field error in field that is not in the form. Field name: {0}. Error: {1}.",
                    fieldname, fielderror)
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
        this.addFieldErrorsToAlertMessageList(formpanel, errors.field, alertmessagelist);
        this.applyFieldErrorsToForm(formpanel, errors.field);
    }
});
