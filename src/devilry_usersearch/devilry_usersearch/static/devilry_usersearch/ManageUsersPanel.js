Ext.define('devilry_usersearch.ManageUsersPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.manageuserspanel',
    cls: 'devilry_usersearch_manageuserspanel',
    requires: [
        'devilry_extjsextras.AlertMessageList',
        //'devilry_usersearch.AutocompleteUserWidget'
    ],

    /**
     * @cfg {String} store (required)
     * The store to autocomplete users from.
     */

    initComponent: function() {
        var deleteLabel = gettext('Loading ...');
        var renameLabel = gettext('Loading ...');


        Ext.apply(this, {
            frame: false,
            border: 0,
            bodyPadding: 40,
            autoScroll: true,

            items: [{
                xtype: 'alertmessagelist'
            }, {
                xtype: 'box',
                html: 'helloworld'
            }]
        });
        this.callParent(arguments);
    }
});
