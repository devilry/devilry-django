/** Singleton class with methods for form error handling. No state is stored in
 * the singleton. */
Ext.define('devilry_extjsextras.form.ErrorUtils', {
    singleton: true,

    _getFieldByName: function(formpanel, fieldname) {
        var fieldComponentQuery = Ext.String.format('[name={0}]', fieldname);
        var match = formpanel.query(fieldComponentQuery);
        if(match.length > 0) {
            return match[0];
        } else {
            return null;
        }
    },

    /**
     * Mark all fields that are both in ``formpanel`` and ``fielderrors`` with
     * using ``field.markInvalid(fielderrors[fieldname])``.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
     * */
    markFieldErrorsAsInvalid: function(formpanel, fielderrors) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var field = this._getFieldByName(formpanel, fieldname);
            if(field) {
                field.markInvalid(fielderrors);
            }
        }, this);
    },

    _getFieldLabel: function(field, fieldname) {
        var displayName = field.fieldLabel;

        // Support label defined in radiogroup
        if(typeof displayName == 'undefined') {
            if(field.getXType() == 'radiofield') {
                var group = field.up('radiogroup');
                displayName = group.fieldLabel;
            }
        }

        // Fall back on the fieldname (the one in the error response object)
        if(typeof displayName == 'undefined') {
            displayName = fieldname;
        }

        return displayName;
    },

    /**
     * Add field errors to ``AlertMessageList``.
     *
     * Locates form field labels using the key in fielderrors, and prefixes all
     * error messages with the field label.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
     * @param alertmessagelist A ``devilry_extjsextras.AlertMessageList`` object.
     * */
    addFieldErrorsToAlertMessageList: function(formpanel, fielderrors, alertmessagelist) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var fielderror = fielderrors.join('. ');
            var field = this._getFieldByName(formpanel, fieldname);
            if(field) {
                var displayName = this._getFieldLabel(field, fieldname);
                var message = Ext.String.format('<strong>{0}:</strong> {1}', displayName, fielderror)
                alertmessagelist.add({
                    message: message,
                    type: 'error'
                });
            } else {
                console.error(Ext.String.format(
                    "Field error in field that is not in the form. Field name: {0}. Error: {1}.",
                    fieldname, fielderror));
            }
        }, this);
    }
});
