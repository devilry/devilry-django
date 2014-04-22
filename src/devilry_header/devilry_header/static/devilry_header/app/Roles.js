Ext.define('devilry_header.Roles', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_roles',
    cls: 'devilryheader_roles',

    tpl: [
        '<tpl if="loading">',
            '<div class="loading">', gettext('Loading'), ' ...</div>',
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
                        '<li><a href="{urlpath_prefix}/devilry_examiner/" class="examiner_role">',
                            '<div class="heading">',
                                gettext('Examiner'),
                            '</div>',
                            '<div class="description">',
                                gettext('Examiners give students feedback on their deliveries.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_subjectadmin | userInfo.is_periodadmin | userInfo.is_assignmentadmin">',
                        '<li><a href="{urlpath_prefix}/devilry_subjectadmin/" class="subjectadmin_role">',
                            '<div class="heading">',
                                interpolate(gettext('%(Subject_term)s administrator'), {
                                    Subject_term: gettext('Subject')
                                }, true),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('%(Subject_term)s administrators manage %(subjects_term)s, %(periods_term)s and assignments where they have been explicitly registered as administrator.'), {
                                    Subject_term: gettext('Subject'),
                                    subjects_term: gettext('subjects'),
                                    nodes_term: gettext('nodes'),
                                    periods_term: gettext('periods')
                                }, true),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                    '<tpl if="userInfo.is_superuser | userInfo.is_nodeadmin">',
                        '<li><a href="{urlpath_prefix}/devilry_nodeadmin/" class="nodeadmin_role">',
                            '<div class="heading">',
                                interpolate(gettext('%(Node_term)s administrator'), {
                                    Node_term: gettext('Node')
                                }, true),
                            '</div>',
                            '<div class="description">',
                                interpolate(gettext('%(Node_term)s administrators manage %(nodes_term)s where they have administrator-rights.'), {
                                    Node_term: gettext('Node'),
                                    nodes_term: gettext('nodes')
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
                                gettext('Superusers have complete access to all data stored in Devilry.'),
                            '</div>',
                        '</a></li>',
                    '</tpl>',
                '</ul>',
                '<p class="bootstrap"><a href="{lacking_permissions_url}">',
                    gettext('I should have had more roles'),
                '</a></p>',
            '<tpl else>',
                '<div class="nopermissions bootstrap">',
                    '<div class="alert alert-error">',
                        gettext('You have no permissions on anything in Devilry. Click <a href="{no_permissions_url}">this link</a> to go to a page explaining how to get access to Devilry.'),
                    '</div>',
                '</div>',
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
