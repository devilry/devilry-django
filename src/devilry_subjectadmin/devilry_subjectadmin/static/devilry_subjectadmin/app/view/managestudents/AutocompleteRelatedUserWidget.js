/** Related User autocomplete widget. */
Ext.define('devilry_subjectadmin.view.managestudents.AutocompleteRelatedUserWidget' ,{
    extend: 'devilry_usersearch.AutocompleteUserWidget',
    alias: 'widget.autocompleterelateduserwidget',
    cls: 'devilry_usersearch_autocompleterelateduserwidget',


    hideTrigger: true,
    displayField: '',
    minChars: 1,

    listGetInnerTpl: function() {
        return[
            '<div class="matchlistitem matchlistitem_{user.username}">',
                '<h3>{user.full_name}</h3>',
                '<small class="username">{user.username}</small>',
                '<tpl if="email">',
                    ' <small class="email">&lt;{user.email}&gt;</small>',
                '</tpl>',
            '</div>'
        ].join('');
    }
});
