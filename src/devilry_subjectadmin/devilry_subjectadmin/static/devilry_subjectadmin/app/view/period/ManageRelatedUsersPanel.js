Ext.define('devilry_subjectadmin.view.period.ManageRelatedUsersPanel' ,{
    extend: 'devilry_usersearch.AbstractManageUsersPanel',
    alias: 'widget.managerelateduserspanel',
    cls: 'devilry_subjectadmin_managerelateduserspanel',
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],

    /**
     * @cfg store
     * The related user store
     */

    /**
     * @cfg {Object} extraColumn
     */

    constructor: function(config) {
        this.callParent([config]);

        this.mon(this.store.proxy, {
            scope: this,
            exception: this._onProxyError
        });
        //this._resetStore();
    },

    initComponent: function() {
        Ext.apply(this, {
            hideHeaders: false,
            columns: [{
                header: 'User',  dataIndex: 'id', flex: 2,
                renderer: Ext.bind(this.renderPrettyformattedUserGridCell, this)
            }, {
                header: 'Tags',  dataIndex: 'tags', flex: 1,
                renderer: Ext.bind(this._renderTagsCell, this)
            }]
        });
        if(this.extraColumn) {
            this.columns.push(this.extraColumn);
        }
        this.callParent(arguments);
    },

    //_resetStore: function() {
        //this.store.removeAll();
        //Ext.each(this.basenodeRecord.get('admins'), function(admin) {
            //this.store.add(admin);
        //}, this);
        //this.store.sort([{
            //sorterFn: function(a, b) {
                //var aKey = a.get('full_name') || a.get('username');
                //var bKey = b.get('full_name') || b.get('username');
                //return aKey.localeCompare(bKey);
            //}
        //}]);
    //},

    _mask: function(message) {
        this.setLoading(message);
    },
    _unmask: function() {
        this.setLoading(false);
    },

    getUserDataFromRecord: function(record) {
        return record.get('user');
    },

    _renderTagsCell: function(unused, unused2, record) {
        return Ext.String.format('<div style="white-space:normal !important;">{0}</div>',
            record.getTagsAsArray().join(', '));
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
        console.log('Add', userRecord);   
        //this._mask('Saving ...');
    },

    removeUsers: function(userRecords) {
        //this._mask(gettext('Saving ...');
        console.log('Remove', userRecords);
    },

    searchMatchesRecord: function(query, record) {
        var match = this.callParent(arguments);
        return match || this.caseIgnoreContains(record.get('tags'), query);
    }
});
