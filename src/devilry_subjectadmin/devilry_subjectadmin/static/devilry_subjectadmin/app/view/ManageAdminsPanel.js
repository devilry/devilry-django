Ext.define('devilry_subjectadmin.view.ManageAdminsPanel' ,{
    extend: 'devilry_usersearch.ManageUsersPanel',
    alias: 'widget.manageadminspanel',
    requires: [
        'devilry_usersearch.ManageUsersGridModel'
    ],

    /**
     * @cfg basenodeRecord
     */

    constructor: function(config) {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry_usersearch.ManageUsersGridModel'
        });
        this.callParent([config]);

        this.mon(this.basenodeRecord.proxy, {
            scope: this,
            exception: this._onProxyError
        });
        this._resetStore();
    },

    _resetStore: function() {
        this.store.removeAll();
        Ext.each(this.basenodeRecord.get('admins'), function(admin) {
            this.store.add(admin);
        }, this);
        this.store.sort('full_name', 'ASC');
    },

    _mask: function(message) {
        this.setLoading(message);
    },
    _unmask: function() {
        this.setLoading(false);
    },

    addUser: function(userRecord) {
        this.basenodeRecord.get('admins').push({
            id: userRecord.get('id')
        });
        
        this._mask('Saving ...');
        this.basenodeRecord.save({
            scope: this,
            success: function() {
                this._onSaveSuccess(userRecord);
            }
        });
        this._resetStore();
    },

    _onSaveSuccess: function(userRecord) {
        this._unmask();
        this._resetStore();
        this.onUserAdded(userRecord);
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        console.error('Save failed', response, operation);
    },
});
