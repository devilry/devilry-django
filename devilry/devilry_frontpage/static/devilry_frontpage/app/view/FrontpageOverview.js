Ext.define('devilry_frontpage.view.FrontpageOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.frontpage_overview',
    cls: 'devilry_frontpage_overview devilry_subtlebg',

    requires: [
        'devilry_header.Roles',
        'devilry_i18n.LanguageSelectWidget'
    ],

    frame: false,
    border: 0,
    padding: '30 0 0 0',
    autoScroll: true,
    layout: 'column',

    items: [{
        xtype: 'box',
        columnWidth: 0.5,
        html: '&nbsp;' // NOTE: We need content for the column to render correctly
    }, {
        xtype: 'container',
        width: 600,
        items: [{
            xtype: 'box',
            padding: '0 0 0 20',
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
            cls: 'devilry_focuscontainer',
            padding: 20,
            items: [{
                xtype: 'box',
                width: 280,
                padding: '0 30 0 0',
                cls: 'bootstrap',
                tpl: [
                    '<h2 style="margin-top: 0; padding-top: 0;">',
                        gettext('Choose your role'),
                    '</h2>',
                    '<p><small class="muted">',
                        gettext('Devilry handles all aspects of the electronic delivery process, including feedback and grading. Each distinct area of responsibilty, or role, has its own user interface. Choose a role from the menu on your right hand side.'),
                    '</small></p>'
                ],
                data: {}
            }, {
                columnWidth: 1,
                xtype: 'devilryheader_roles',
                margin: '6 0 10 0'
            }]
        }]
    }, {
        xtype: 'container',
        itemId: 'sidebar',
        width: 260,
        padding: '25 0 0 50',
        items: [{
            xtype: 'container',
            itemId: 'selectLanguage',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                html: ['<h4>', gettext('Language'), '</h4>'].join('')
            }, {
                xtype: 'devilry_i18n_languageselect'
            }]
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            itemId: 'needHelp',
            margin: '30 0 0 0',
            html: [
                '<h4>',
                    gettext('Need help?'),
                '</h4>',
                '<p class="muted">',
                    gettext('Click on your name in the top right corner of the page.'),
                '</p>'
            ].join('')
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            itemId: 'improveDevilry',
            margin: '30 0 0 0',
            tpl: [
                '<h4>',
                    gettext('Improve Devilry?'),
                '</h4>',
                '<p class="muted">',
                    gettext('Devilry is an open source general purpose electronic assignment delivery and feedback system. Visit <a href="{devilryurl}">{devilryurl}</a> and help us make it better.'),
                '</p>'
            ],
            data: {
                devilryurl: 'http://devilry.org'
            }
        }]
    }, {
        xtype: 'box',
        columnWidth: 0.5,
        html: '&nbsp;' // NOTE: We need content for the column to render correctly
    }]
});
