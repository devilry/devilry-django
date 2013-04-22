Ext.define('devilry_subjectadmin.utils.Breadcrumbs', {
    extend: 'devilry_header.Breadcrumbs',
    requires: ['devilry_subjectadmin.utils.UrlLookup'],

    /**
     * @cfg {devilry_authenticateduserinfo.UserInfoModel} [userInfoRecord]
     */

    getDefaultBreadcrumbs: function () {
        var dashboardLinks = [];
        
        if(this.userInfoRecord.isSubjectPeriodOrAssignmentAdmin()) {
            dashboardLinks.push({
                text: gettext("Subjectadmin"),
                url: '#'
            });
        }
        if(this.userInfoRecord.get('is_superuser') || this.userInfoRecord.get('is_nodeadmin')) {
            dashboardLinks.push({
                text: gettext("Nodeadmin"),
                url: devilry_subjectadmin.utils.UrlLookup.nodeadminDashboard()
            });
        }
        return [dashboardLinks];
    },

    formatUrl: function (url, meta) {
        return url;
    }
});
