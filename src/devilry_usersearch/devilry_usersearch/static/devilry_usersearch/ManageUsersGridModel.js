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
    ]
});
