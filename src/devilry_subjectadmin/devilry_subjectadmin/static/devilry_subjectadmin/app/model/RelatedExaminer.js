Ext.define('devilry_subjectadmin.model.RelatedExaminer', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'user_id',  type: 'int'},
        {name: 'user__username',  type: 'string'},
        {name: 'user__email',  type: 'string'},
        {name: 'user__devilryuserprofile__full_name',  type: 'string'},
        {name: 'tags', type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/subjectadmin/rest/relatedexaminer/',
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
