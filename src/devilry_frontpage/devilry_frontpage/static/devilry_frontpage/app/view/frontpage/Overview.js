Ext.define('devilry_frontpage.view.frontpage.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.overview',
    cls: 'devilry_frontpage_overview',

    requires: [
        'devilry_header.Roles',

    ],

    frame: false,
    border: 0,
    bodyPadding: 20,
    autoScroll: true,
    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    items: [{
        xtype: 'box',
        flex: 1
    }, {
        xtype: 'container',
        width: 560,
        items: [{
            xtype: 'box',
            itemId: 'logo',
            tpl: [
                '<img src="{staticprefix}/devilry_frontpage/resources/images/logoandtext.png"/>'
            ],
            data: {
                staticprefix: DevilrySettings.DEVILRY_STATIC_URL
            }
        }, {
            xtype: 'container',
            margin: '40 0 0 0',
            layout: 'column',
            items: [{
                xtype: 'box',
                width: 280,
                padding: '0 20 0 0',
                cls: 'bootstrap',
                tpl: [
                    '<h2>',
                        gettext('Choose your role'),
                    '</h2>',
                    '<p><small>',
                        gettext('Devilry handles all aspects of the electronic delivery process. Each distinct area of responsibilty, or role, has its own user interface. Choose your role from the menu on your right hand side.'),
                    '</small></p>'
                ],
                data: {
                }
            }, {
                columnWidth: 1,
                xtype: 'devilryheader_roles'
            }]
        }]
    }, {
        xtype: 'container',
        itemId: 'sidebar',
        width: 260,
        padding: '25 0 0 50',
        items: [{
            xtype: 'textfield',
            emptyText: 'Language: ',
            width: 300
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            itemId: 'needHelp',
            margin: '30 0 0 0',
            html: [
                '<h3>',
                    gettext('Need help?'),
                '</h3>',
                '<p>',
                    gettext('Click on your name in the top right corner of the page.'),
                '</p>'
            ].join('')
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            itemId: 'improveDevilry',
            margin: '30 0 0 0',
            html: [
                '<h3>',
                    gettext('Improve Devilry?'),
                '</h3>',
                '<p>',
                    gettext('Devilry is an open source general purpose assignment delivery system. Visit http://devilry.org and help us make it better.'),
                '</p>'
            ].join('')
        }]
    }, {
        xtype: 'box',
        flex: 1
    }]
});
