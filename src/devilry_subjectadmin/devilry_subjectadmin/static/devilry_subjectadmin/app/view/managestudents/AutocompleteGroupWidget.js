/** Related User autocomplete widget. */
Ext.define('devilry_subjectadmin.view.managestudents.AutocompleteGroupWidget', {
    extend: 'devilry_usersearch.AutocompleteUserWidget',
    alias: 'widget.autocompletegroupwidget',
    cls: 'devilry_usersearch_autocompletegroupwidget',

    hideTrigger: true,
    displayField: 'id',
    minChars: 1,
    store: 'SearchForGroups',

    //fieldLabel: gettext('Select by search'),
    //labelWidth: 120,
    hideLabel: true,

    listGetInnerTpl: function() {
        return[
            '<div class="matchlistitem matchlistitem_{id}">',
                '<ul class="unstyled">',
                '<tpl for="candidates">',
                    '<li>',
                        '<tpl if="user.full_name">',
                            '<strong>{user.full_name}',
                            ' <small>({user.username})</small>',
                        '<tpl else>',
                            '<strong>{user.username}',
                        '</tpl>',
                    '</li>',
                '</tpl>',
                '</ul>',
            '</div>'
        ].join('');
    }
});
