/**
 * A dialog for deleting a record using and DjangoRestframeworkProxyErrorMixin
 * to handle errors.
 * */
Ext.define('devilry_subjectadmin.view.DeleteDjangoRestframeworkRecordDialog', {
    extend: 'devilry_extjsextras.ConfirmDeleteDialog',
    mixins: {
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },

    statics: {
        showIfCanDelete: function(options) {
            if(options.basenodeRecord.get('can_delete')) {
                Ext.create('devilry_subjectadmin.view.DeleteDjangoRestframeworkRecordDialog', options).show();
            } else {
                var msg = gettext('You do not have permissions required to delete {short_description}. Only superusers can delete non-empty items. You can only delete items where you are admin on an item higher up in the hierarchy.');
                Ext.Msg.show({
                    title: gettext('Permission denied'),
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: Ext.create('Ext.XTemplate', msg).apply({
                        short_description: options.short_description
                    })
                });
            }
        }
    },

    /**
     * @cfg {Ext.data.Model} basenodeRecord (required)
     */

    initComponent: function() {
        this.addEvents({
            /**
             * @event
             * Fired when the record has been deleted successfully.
             * */
            "deleteSuccess" : true
        });

        this.callParent(arguments);
        this.mon(this.basenodeRecord.proxy, {
            scope:this,
            exception: this._onProxyError
        });
        this.on({
            scope: this,
            deleteConfirmed: this._onDeleteConfirmed
        });
    },

    _onProxyError: function(proxy, response, operation) {
        var alertmessagelist = this.down('alertmessagelist');
        var form = this.down('form');
        this.handleProxyError(alertmessagelist, form, response, operation);
    },

    _onDeleteConfirmed: function() {
        this.basenodeRecord.destroy({
            scope: this,
            success: this._onDeleteSuccessful
        });
    },

    _onDeleteSuccessful: function() {
        this.fireEvent('deleteSuccess');
        this.close();
    }
});
