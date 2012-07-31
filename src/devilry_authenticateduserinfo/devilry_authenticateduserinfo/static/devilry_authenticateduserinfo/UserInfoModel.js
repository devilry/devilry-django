Ext.define('devilry_authenticateduserinfo.UserInfoModel', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'full_name',  type: 'string'}
    ],

    proxy: {
        type: 'ajax',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_authenticateduserinfo/userinfo',
        reader: {
            type: 'json'
        }
    }
});
