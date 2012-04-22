/**
 * Group-model for the ``/subjectadmin/rest/group`` API.
 */
Ext.define('devilry_subjectadmin.model.Group', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'num_deliveries', type: 'int'},
        {name: 'name',  type: 'string'},
        {name: 'is_open',  type: 'boolean'},
        {name: 'feedback__grade',  type: 'string'},
        {name: 'feedback__points',  type: 'string'},
        {name: 'feedback__save_timestamp',  type: 'date'},
        {name: 'feedback__is_passing_grade',  type: 'boolean'},
        {name: 'students', type: 'auto'},
        {name: 'examiners', type: 'auto'},
        {name: 'deadlines', type: 'auto'},
        {name: 'tags', type: 'auto'},
    ],

    proxy: {
        type: 'rest',
        baseurl: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/subjectadmin/rest/group/',
        url: null, // We use baseurl to dynamically set the url suffixed with assignmentid
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json',
            //root: 'items',
            //record: 'item'
        }
    }
});
