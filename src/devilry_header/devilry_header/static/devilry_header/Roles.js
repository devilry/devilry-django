Ext.define('devilry_header.Roles', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_roles',

    tpl: [
        '<h2>',
            gettext('Choose your role'),
        '</h2>',
        '<p class="discreet">',
            gettext('All available roles are listed below. Use the link below the list of roles if you are missing any permissions.'),
        '</p>',
        '<a href="{lacking_permissions_link}">',
            gettext('I should have had more permissions'),
        '</a>'
    ],

    data: {
        lacking_permissions_link: '#'
    }
});
