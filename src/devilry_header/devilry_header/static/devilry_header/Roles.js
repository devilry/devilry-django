Ext.define('devilry_header.Roles', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_roles',
    cls: 'devilryheader_roles',

    tpl: [
        '<tpl if="loading">',
            '<p>', gettext('Loading'), ' ...</p>',
        '<tpl else>',
            '<tpl if="has_any_roles">',
                '<ul role="navigation">',
                    '<tpl if="userInfo.is_student">',
                        '<li><a href="{urlpath_prefix}/devilry_student/" class="student_role">',
                            '<div class="heading">',
                                gettext('Student'),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('Students can make %(deliveres_term)s and browse their own feedback history.'), {
                                    deliveres_term: gettext('deliveries')
                                }, true),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_examiner">',
                        '<li><a href="{urlpath_prefix}/examiner/" class="examiner_role">',
                            '<div class="heading">',
                                gettext('Examiner'),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('Examiners give students %(feedback_term)s on their %(deliveries_term)s.'), {
                                    feedback_term: gettext('feedback'),
                                    deliveries_term: gettext('deliveries')
                                }, true),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser | userInfo.is_nodeadmin | userInfo.is_subjectadmin | userInfo.is_periodadmin | userInfo.is_assignmentadmin">',
                        '<li><a href="{urlpath_prefix}/administrator/" class="administrator_role">',
                            '<div class="heading">',
                                gettext('Administrator'),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('Administrators manage %(subjects_term)s, %(nodes_term)s, %(periods_term)s and %(assignments_term)s where they have been explicitly registered as administrator.'), {
                                    subjects_term: gettext('subjects'),
                                    nodes_term: gettext('nodes'),
                                    periods_term: gettext('periods'),
                                    assignments_term: gettext('assignments')
                                }, true),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser">',
                        '<li><a href="{urlpath_prefix}/superuser/" class="superuser_role">',
                            '<div class="heading">',
                                gettext('Superuser'),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('%(Superusers_term)s have complete access to all data stored in Devilry.'), {
                                    Superusers_term: gettext('Superusers')
                                }, true),
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
