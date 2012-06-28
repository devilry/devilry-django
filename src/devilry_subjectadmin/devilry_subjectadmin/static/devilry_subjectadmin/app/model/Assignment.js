/** Assignment model. */
Ext.define('devilry_subjectadmin.model.Assignment', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'admins',  type: 'auto'},
        {name: 'breadcrumb',  type: 'auto'},
        {name: 'can_delete',  type: 'bool'},
        {name: 'etag',  type: 'string'},
        {name: 'first_deadline',  type: 'date'},
        {name: 'id', type: 'auto'},
        {name: 'inherited_admins',  type: 'auto'},
        {name: 'long_name',  type: 'string'},
        {name: 'parentnode', type: 'auto'},
        {name: 'publishing_time',  type: 'date'},
        {name: 'short_name',  type: 'string'},
        {name: 'scale_points_percent',  type: 'int'},
        {name: 'delivery_types',  type: 'int'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/assignment/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
