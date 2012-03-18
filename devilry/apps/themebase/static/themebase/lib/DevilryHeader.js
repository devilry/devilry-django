/**
 * Devilry page header with the role tabs and log in/out links.
 */
Ext.define('themebase.DevilryHeader', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.devilryheader',
    //bodyStyle: 'background-color: transparent !important',
    ui: 'transparentpanel',
    border: false,
    margins: '0 0 0 0',
    height: 49,
    //autoHeight: true,

    /**
     * @cfg {string} navclass (required)
     */

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="devilryheader">',
            '<div id="heading" style="z-index: 1000;">',
                '<div id="authenticated-user-bar">',
                    '<tpl if="DevilryUser.is_authenticated">',
                        '<span id="authenticated-user-info">',
                            '{DevilryUser.username}',
                        '</span>',
                        ' | <a class="loginout-link" href="{DevilrySettings.DEVILRY_LOGOUT_URL}">Log out</a>',
                    '</tpl>',
                    '<tpl if="!DevilryUser.is_authenticated">',
                        '<a class="loginout-link" href="{DevilrySettings.DEVILRY_LOGIN_URL}">Log in</a>',
                    '</tpl>',
                '</div>',
                '<h1>Devilry</h1>',
            '</div>',
            '<div class="nav {navclass}">',
                '<ul>',
                    //'<li class="student-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/student/">',
                        //dtranslate('themebase.role.student.title'),
                    //'</a></li>',
                    //'<li class="examiner-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/examiner/">',
                        //dtranslate('themebase.role.examiner.title'),
                    //'</a></li>',
                    '<li class="subjectadmin-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/subjectadmin/ui#">',
                        dtranslate('themebase.role.subjectadmin.title'),
                    '</a></li>',
                    //'<li class="oldadmin-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/administrator/">',
                        //'Administrator (old UI)',
                    //'</a></li>',
                    '<li class="externallink-navitem"><a href="{DevilrySettings.DEVILRY_HELP_URL}" target="_blank">',
                        dtranslate('themebase.helplink.title'),
                    '</a></li>',
                '</ul>',
            '</div>',
        '</div>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.html = this.bodyTpl.apply({
            navclass: this.navclass,
            DevilrySettings: DevilrySettings,
            DevilryUser: DevilryUser
        });
        this.callParent(arguments);
    }
});
