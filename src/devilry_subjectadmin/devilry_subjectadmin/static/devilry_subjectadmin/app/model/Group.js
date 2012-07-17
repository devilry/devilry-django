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
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/group/{0}',
        url: null, // We use urlpatt to dynamically generate the url
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
