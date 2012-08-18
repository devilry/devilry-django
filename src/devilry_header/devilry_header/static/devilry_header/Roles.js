Ext.define('devilry_header.Roles', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_roles',
    cls: 'devilryheader_roles',

    tpl: [
        '<tpl if="loading">',
            '<p>', gettext('Loading ...'), '</p>',
        '<tpl else>',
            '<tpl if="has_any_roles">',
                '<ul role="navigation">',
                    '<tpl if="userInfo.is_student">',
                        '<li><a href="{urlpath_prefix}/devilry_student/" class="student_role">',
                            '<div class="heading">',
                                gettext('Student'),
                            '</div>',
                            '<div class="description">',
                                gettext('Students can make deliveres and browse their own feedback history.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_examiner">',
                        '<li><a href="{urlpath_prefix}/examiner/" class="examiner_role">',
                            '<div class="heading">',
                                gettext('Examiner'),
                            '</div>',
                            '<div class="description">',
                                gettext('Examiners give students feedback on their deliveries.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser | userInfo.is_nodeadmin | userInfo.is_subjectadmin | userInfo.is_periodadmin | userInfo.is_assignmentadmin">',
                        '<li><a href="{urlpath_prefix}/administrator/" class="administrator_role">',
                            '<div class="heading">',
                                gettext('Administrator'),
                            '</div>',
                            '<div class="description">',
                                gettext('Administrators manage nodes, subjects, periods and assignments where they have been explicitly registered as administrator.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser">',
                        '<li><a href="{urlpath_prefix}/superuser/" class="superuser_role">',
                            '<div class="heading">',
                                gettext('Superuser'),
                            '</div>',
                            '<div class="description">',
                                gettext('Superusers have complete access to all data stored in Devilry. Superusers are also automatically granted access to anything administrators have access to, so you are able to choose Administrator as well as Superuser.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                '</ul>',
                '<p class="bootstrap"><a href="{lacking_permissions_url}">',
                    gettext('I should have had more roles'),
                '</a></p>',
            '<tpl else>',
                '<p class="nopermissions bootstrap">',
                    gettext('You have no permissions on anything in Devilry. Click <a href="{no_permissions_url}">this link</a> to go to a page explaining how to get access to Devilry.'),
                '</p>',
            '</tpl>',
        '</tpl>'
    ],

    data: {
        loading: true
    },


    /**
     * Set UserInfo record and update view.
     */
    setUserInfoRecord: function(userInfoRecord) {
        this.update({
            userInfo: userInfoRecord.data,
            has_any_roles: userInfoRecord.hasAnyRoles(),
            lacking_permissions_url: DevilrySettings.DEVILRY_LACKING_PERMISSIONS_URL,
            urlpath_prefix: DevilrySettings.DEVILRY_URLPATH_PREFIX,
            no_permissions_url: DevilrySettings.DEVILRY_LACKING_PERMISSIONS_URL
        });
    }
});
