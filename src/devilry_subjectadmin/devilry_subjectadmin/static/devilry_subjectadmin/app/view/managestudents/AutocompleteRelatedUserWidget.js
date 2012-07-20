/** Related User autocomplete widget. */
Ext.define('devilry_subjectadmin.view.managestudents.AutocompleteRelatedUserWidget' ,{
    extend: 'devilry_usersearch.AutocompleteUserWidget',
    alias: 'widget.autocompleterelateduserwidget',
    cls: 'devilry_usersearch_autocompleterelateduserwidget',


    hideTrigger: false,
    displayField: 'id',
    minChars: 1,

    emptyText: gettext('Select a user from the list, or search for username, full name or email...'),

    listGetInnerTpl: function() {
        return[
            '<div class="matchlistitem matchlistitem_{user.username}">',
                '<h3>{user.full_name}</h3>',
                '<small class="username">{user.username}</small>',
                '<tpl if="user.email">',
                    ' <small class="user.email">&lt;{user.email}&gt;</small>',
                '</tpl>',
            '</div>'
        ].join('');
    }
});
