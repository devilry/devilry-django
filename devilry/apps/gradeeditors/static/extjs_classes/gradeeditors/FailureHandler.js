Ext.define('devilry.gradeeditors.FailureHandler', {
    statics: {
        onFailure: function(records, operation) {
            var title = 'Failed to save!';
            var msg = 'Please try again';
            var icon = Ext.Msg.ERROR;
            if(operation.error.status === 0) {
                title = 'Server error';
                msg = 'Could not contact the server. Please try again.';
            } else if(operation.error.status === 400) {
                title = 'Failed to save!';
                msg = operation.responseData.items.errormessages[0];
                icon = Ext.Msg.WARNING;
            }
            Ext.MessageBox.show({
                title: title,
                msg: msg,
                buttons: Ext.Msg.OK,
                icon: icon,
                closable: false
            });
        }
    }
});
