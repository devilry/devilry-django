/** Period model. */
Ext.define('devilry_subjectadmin.model.Period', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'auto'},
        {name: 'parentnode', type: 'auto'},
        {name: 'short_name',  type: 'string'},
        {name: 'long_name',  type: 'string'},
        {name: 'can_delete',  type: 'bool'},
        {name: 'etag',  type: 'string'},
        {name: 'admins',  type: 'auto'},
        {name: 'inherited_admins',  type: 'auto'},
        {name: 'start_time',  type: 'auto'},
        {name: 'end_time',  type: 'auto'},
        {name: 'breadcrumb',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/period/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
