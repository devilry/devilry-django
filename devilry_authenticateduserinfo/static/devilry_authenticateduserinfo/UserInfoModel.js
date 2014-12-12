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
        {name: 'is_subjectadmin',  type: 'bool'},
        {name: 'is_periodadmin',  type: 'bool'},
        {name: 'is_assignmentadmin',  type: 'bool'},
        {name: 'is_student',  type: 'bool'},
        {name: 'is_examiner',  type: 'bool'}
    ],

    proxy: {
        type: 'ajax',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_authenticateduserinfo/userinfo',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    /** Returns true is the user has any roles. */
    hasAnyRoles: function() {
        return this.get('is_superuser') || this.get('is_nodeadmin') ||
            this.get('is_subjectadmin') || this.get('is_periodadmin') || this.get('is_assignmentadmin') ||
            this.get('is_student') || this.get('is_examiner');
    },

    isAdmin:function () {
        return this.get('is_superuser') || this.get('is_nodeadmin') || this.isSubjectPeriodOrAssignmentAdmin();
    },

    isSubjectPeriodOrAssignmentAdmin: function () {
        return this.get('is_subjectadmin') || this.get('is_periodadmin') || this.get('is_assignmentadmin');
    },

    getDisplayName: function() {
        return this.get('full_name') || this.get('username');
    }
});
