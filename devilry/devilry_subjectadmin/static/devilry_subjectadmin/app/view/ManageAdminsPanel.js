Ext.define('devilry_subjectadmin.view.ManageAdminsPanel' ,{
    extend: 'devilry_usersearch.AbstractManageUsersPanel',
    alias: 'widget.manageadminspanel',
    cls: 'devilry_subjectadmin_manageadminspanel',
    requires: [
        'devilry_usersearch.ManageUsersGridModel',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
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
        this.store.sort([{
            sorterFn: function(a, b) {
                var aKey = a.get('full_name') || a.get('username');
                var bKey = b.get('full_name') || b.get('username');
                return aKey.localeCompare(bKey);
            }
        }]);
    },

    _mask: function(message) {
        this.setLoading(message);
    },
    _unmask: function() {
        this.setLoading(false);
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(response, operation);
        var errormessage = error.asHtmlList();
        Ext.widget('htmlerrordialog', {
            bodyHtml: errormessage
        }).show();
    },

    addUser: function(userRecord) {
        this.basenodeRecord.get('admins').push({
            id: userRecord.get('id')
        });
        
        this._mask(gettext('Saving') + ' ...');
        this.basenodeRecord.save({
            scope: this,
            success: function() {
                this._unmask();
                this._resetStore();
                this.onUserAdded(userRecord);
            }
        });
    },

    /* Get the remaining records after removing the given userRecords */
    _getRemainingAfterRemove: function(userRecords) {
        var deleteIds = [];
        Ext.each(userRecords, function(userRecord) {
            deleteIds.push(userRecord.get('id'));
        });
        var remainingAdmins = [];
        Ext.each(this.basenodeRecord.get('admins'), function(admin) {
            if(deleteIds.indexOf(admin.id) == -1) {
                remainingAdmins.push(admin);
            }
        });
        return remainingAdmins;
    },

    removeUsers: function(userRecords) {
        var remainingAdmins = this._getRemainingAfterRemove(userRecords);
        this.basenodeRecord.set('admins', remainingAdmins);
        this._mask(gettext('Saving') + ' ...');
        this.basenodeRecord.save({
            scope: this,
            success: function() {
                this._unmask();
                this._resetStore();
                this.onUsersRemoved(userRecords);
            }
        });
    }
});
