Ext.define('devilry_header.UserInfoBox', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_userinfobox',
    cls: 'devilryheader_userinfobox',

    tpl: [
        '<h2>',
            gettext('About you'),
        '</h2>',
        '<tpl if="loading">',
            '<p>', gettext('Loading'), ' ...</p>',
        '<tpl else>',
            '<p class="discreet">',
                gettext('The table below shows the personal information registered about you in Devilry. <a href="{wrong_userinfo_url}">Click here</a> if any information is incorrect.'),
            '</p>',
            '<table class="userinfotable">',
                '<tbody>',
                    '<tr>',
                        '<th>', gettext('Name'), ':</th>',
                        '<td>{userInfo.full_name}</td>',
                    '</tr>',
                    '<tr>',
                        '<th>', gettext('Email'), ':</th>',
                        '<td>{userInfo.email}</td>',
                    '</tr>',
                    '<tr>',
                        '<th>', gettext('Username'), ':</th>',
                        '<td>{userInfo.username}</td>',
                    '</tr>',
                '</tbody>',
            '</table>',
            '<div class="logout_para bootstrap"><a href="{logout_url}" class="logout_button btn btn-primary btn-large">',
                gettext('Log out'),
            '</a></div>',
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
            wrong_userinfo_url: DevilrySettings.DEVILRY_WRONG_USERINFO_URL,
            logout_url: DevilrySettings.DEVILRY_LOGOUT_URL
        });
    }
});
