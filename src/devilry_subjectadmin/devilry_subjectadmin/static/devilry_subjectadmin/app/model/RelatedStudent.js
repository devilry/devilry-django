Ext.define('devilry_subjectadmin.model.RelatedStudent', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'candidate_id',  type: 'string'},
        {name: 'user_id',  type: 'int'},
        {name: 'user__username',  type: 'string'},
        {name: 'user__email',  type: 'string'},
        {name: 'user__devilryuserprofile__full_name',  type: 'string'},
        {name: 'tags', type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/subjectadmin/rest/relatedstudent/',
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
