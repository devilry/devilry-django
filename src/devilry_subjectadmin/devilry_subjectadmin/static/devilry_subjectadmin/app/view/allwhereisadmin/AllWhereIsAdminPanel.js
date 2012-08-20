Ext.define('devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.allwhereisadminpanel', // Define the widget xtype as allwhereisadminpanel
    cls: 'dashboard',

    frame: false,
    border: 0,
    bodyPadding: 40,
    autoScroll: true, // Autoscroll on overflow

    items: [{
        xtype: 'box',
        tpl: [ // Refer to Ext.XTemplate docs for info about the template format
            '<tpl if="loadingtext">',
                '{loadingtext}',
            '<tpl else>',
                'Loaded (TODO: use update the view with a tree of available data)',
            '</tpl>',
            
        ],
        itemId: 'listOfSubjects', // itemId is like a HTML ID, however it is only unique within this container. Can be used in component queries/selectors
        data: {
            loadingtext: gettext('Loading') + ' ...' // Use gettext() to mark strings for translation
        }
    }]
});
