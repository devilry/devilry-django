/** A model that works out of the box with ManageUsersGrid. Useful as
 * documentation, and for local stores for the grid. */
Ext.define('devilry_usersearch.ManageUsersGridModel', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'username',  type: 'string'},
        {name: 'full_name',  type: 'string'},
        {name: 'email',  type: 'string'}
    ],

    getDisplayName: function() {
        if(Ext.isEmpty(this.get('full_name'))) {
            return this.get('username');
        } else {
            return this.get('full_name');
        }
    },

    statics: {
        /** Returns a template that can be used to pretty-format a ManageUsersGridModel object in a grid cell. */
        gridCellXTemplate: function() {
            return Ext.create('Ext.XTemplate',
                '<div class="prettyformattedusercell prettyformattedusercell_{username}">',
                '   <div class="full_name"><strong>{full_name}</strong></div>',
                '   <tpl if="!full_name">',
                '       <strong class="username">{username}</strong>',
                '       <small>(', gettext('Full name missing') ,')</small>',
                '   </tpl>',
                '   <div class="username_and_email">',
                '       <tpl if="full_name">',
                '           <small class="username">{username}</small>',
                '       </tpl>',
                '       <tpl if="email">',
                '          <small class="email">&lt;{email}&gt;</small>',
                '       </tpl>',
                '   </div>',
                '</div>'
            );
        }
    }
});
