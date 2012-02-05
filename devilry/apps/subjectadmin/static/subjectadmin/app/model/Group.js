Ext.define('subjectadmin.model.Group', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
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
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/subjectadmin/rest/group/',
        extraParams: {
            _devilry_accept: 'application/json'
        },
        reader: {
            type: 'json',
            //root: 'items',
            //record: 'item'
        }
    }
});
