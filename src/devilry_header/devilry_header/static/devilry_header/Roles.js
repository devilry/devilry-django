Ext.define('devilry_header.Roles', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_roles',
    cls: 'devilryheader_roles',

    tpl: [
        '<tpl if="loading">',
            '<p>', gettext('Loading ...'), '</p>',
        '<tpl else>',
            '<h2>',
                gettext('Choose your role'),
            '</h2>',
            '<tpl if="userInfo">',
                '<p class="discreet">',
                    gettext('All your available roles are listed below.'),
                '</p>',
                '<ul role="navigation">',
                    '<li><a href="{urlpath_prefix}/student/" class="student_role">',
                        '<div class="heading">',
                            gettext('Student'),
                        '</div>',
                        '<div class="description">',
                            gettext('Students can make deliveres and browse their own feedback history.'),
                        '</div>',
                    '</a></li>',
                    '<li><a href="{urlpath_prefix}/examiner/" class="examiner_role">',
                        '<div class="heading">',
                            gettext('Examiner'),
                        '</div>',
                        '<div class="description">',
                            gettext('Examiners give students feedback on their deliveries.'),
                        '</div>',
                    '</a></li>',
                    '<li><a href="{urlpath_prefix}/administrator/#" class="administrator_role">',
                        '<div class="heading">',
                            gettext('Administrator'),
                        '</div>',
                        '<div class="description">',
                            gettext('Administrators manage nodes, subjects, periods and assignments where they have been explicitly registered as administrator.'),
                        '</div>',
                    '</a></li>',
                    '<li><a href="{urlpath_prefix}/administrator/#" class="superuser_role">',
                        '<div class="heading">',
                            gettext('Superuser'),
                        '</div>',
                        '<div class="description">',
                            gettext('Superusers have complete access to all data stored in Devilry.'),
                        '</div>',
                    '</a></li>',
                '</ul>',
                '<p><a href="{lacking_permissions_url}">',
                    gettext('I should have had more roles'),
                '</a></p>',
            '<tpl else><p class="nopermissions">',
                gettext('You have no permissions on anything in Devilry. Click <a href="{no_permissions_url}">this link</a> to go to a page explaining how to get access to Devilry.'),
            '</p></tpl>',
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
            lacking_permissions_url: '#',
            urlpath_prefix: DevilrySettings.DEVILRY_URLPATH_PREFIX,
            no_permissions_url: '#'
        });
    }
});
