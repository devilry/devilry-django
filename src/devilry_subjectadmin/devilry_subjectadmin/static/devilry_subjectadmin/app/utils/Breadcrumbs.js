Ext.define('devilry_subjectadmin.utils.Breadcrumbs', {
    extend: 'devilry_header.Breadcrumbs',

    /**
     * @cfg {devilry_authenticateduserinfo.UserInfoModel} [userInfoRecord]
     */

    getDefaultBreadcrumbs:function () {
        return this.defaultBreadcrumbs;
    }
});