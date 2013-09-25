Ext.define('devilry_nodeadmin.view.dashboard.DashboardOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.dashboardoverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    requires: [
        'devilry_usersearch.AutocompleteUserWidget'
    ],

    layout: 'column',
    autoScroll: true,

    items: [{
        xtype: 'container',
        padding: '30 20 20 30',
        columnWidth: 1.0,
        items: [{
            xtype: 'toplevelnodelist'
        }, {
            xtype: 'container',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                margin: '15 0 4px 0',
                html: [
                    '<strong>',
                        gettext('Find details about a student:'),
                    '</strong>'
                ].join('')
            }, {
                xtype: 'autocompleteuserwidget',
                itemId: 'userSearchBox',
                fieldLabel: '',
                emptyText: gettext('Search by name, username or email...'),
                width: 300
            }] 
        }]
    }, {
        xtype: 'betawarning',
        width: 250,
        padding: '30 20 20 30'
    }]
});
