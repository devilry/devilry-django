Ext.define('devilry_authenticateduserinfo.UserInfoModel', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'username',  type: 'string'},
        {name: 'full_name',  type: 'string'},
        {name: 'email',  type: 'string'},
        {name: 'languagecode',  type: 'string'},
        {name: 'is_superuser',  type: 'bool'},
        {name: 'is_nodeadmin',  type: 'bool'},
        {name: 'is_periodadmin',  type: 'bool'},
        {name: 'is_assignmentadmin',  type: 'bool'},
        {name: 'is_student',  type: 'bool'},
        {name: 'is_examiner',  type: 'bool'}
    ],

    proxy: {
        type: 'ajax',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_authenticateduserinfo/userinfo',
        reader: {
            type: 'json'
        }
    }
});
