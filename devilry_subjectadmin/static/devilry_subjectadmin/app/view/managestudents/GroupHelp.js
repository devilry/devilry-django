Ext.define('devilry_subjectadmin.view.managestudents.GroupHelp', {
    singleton: true,

    getGroupInfoColHelp: function() {
        return [
            '<p>',
                gettext('Each group is listed with full names first, then usernames, and lastly we display their status.'),
                ' ',
                gettext('The status of a group is one of:'),
            '</p>',
            this._getStatusDescriptionList()
        ].join('');
    },

    _getStatusDescriptionList: function() {
        return [
            '<ul>',
                '<li>',
                    '<em>', gettext('Active grade'), '</em>',
                    ' &mdash; <small>', gettext('If the examiner(s) has completed correcting the group. This is the active grade for the group on this assignment, which is not always their active grade on the current deadline.'), '</small>',
                '</li>',
                '<li>',
                    '<em>', gettext('Waiting for feedback'), '</em>',
                    ' &mdash; <small>', gettext('If their active deadline has expired, and they have not been given any feedback.'), '</small>',
                '</li>',
                '<li>',
                    '<em>', gettext('Waiting for deliveries'), '</em>',
                    ' &mdash; <small>', gettext('If their active deadline has not expired.'), '</small>',
                '</li>',
                '<li class="muted"><small>',
                    gettext('You may get other status-messages. In that case there is probably an error with some system integrating itself with Devilry, or a bug in Devilry.'),
                '</small></li>',
            '</ul>'
        ].join('');
    }
});

