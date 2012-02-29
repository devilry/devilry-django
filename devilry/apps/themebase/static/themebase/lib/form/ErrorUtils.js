/** Singleton class with methods for form error handling. No state is stored in
 * the singleton. */
Ext.define('themebase.form.ErrorUtils', {
    singleton: true,

    /**
     * Mark all fields that are both in ``formpanel`` and ``fielderrors`` with
     * using ``field.markInvalid(fielderrors[fieldname])``.
     *
     * @param formpanel A ``Ext.form.Panel`` object.
     * @param fielderrors Such as the one returned by ``getRestfulErrorsFromOperation``.
     * */
    markFieldErrorsAsInvalid: function(formpanel, fielderrors) {
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
    }
});
