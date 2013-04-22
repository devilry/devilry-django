Ext.define('devilry_subjectadmin.utils.Breadcrumbs', {
    extend: 'devilry_header.Breadcrumbs',

    /**
     * @cfg {devilry_authenticateduserinfo.UserInfoModel} [userInfoRecord]
     */

    getDefaultBreadcrumbs:function () {
        return [{
            text: gettext("Subjectadmin"),
            url: '#'
        }];
    },

    formatUrl: function (url, meta) {
        return url;
    }
});
