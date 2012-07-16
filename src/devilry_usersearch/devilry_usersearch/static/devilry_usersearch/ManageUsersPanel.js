Ext.define('devilry_usersearch.ManageUsersPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.manageuserspanel',
    cls: 'devilry_usersearch_manageuserspanel',
    requires: [
        'devilry_usersearch.AutocompleteUserWidget'
    ],

    initComponent: function() {
        this.store = Ext.create('devilry_usersearch.UserSearchStore');

        Ext.apply(this, {
            frame: false,
            border: 0,
            layout: 'border',
            items: [{
                xtype: 'container',
                region: 'center',
                html: 'list of users'
            }, {
                xtype: 'container',
                layout: 'fit',
                region: 'south',
                height: 36,
                padding: 4,
                items: {
                    xtype: 'autocompleteuserwidget',
                    listeners: {
                        scope: this,
                        userSelected: this._onSelectUser
                    }
                }
            }]
        });
        this.callParent(arguments);
    },

    _onSelectUser: function(combo, userRecord) {
        console.log(userRecord);
    }
});
