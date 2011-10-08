Ext.define('devilry.extjshelpers.page.Header', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.pageheader',
    bodyStyle: 'background-color: transparent !important',
    border: false,
    margins: '0 0 0 0',
    height: 90,
    //autoHeight: true,

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="header">',
        '    <div id="heading">',
        '        <h1>Devilry</h1>',
        '        <div id="authenticated-user-bar">',
        '            <tpl if="DevilryUser.is_authenticated">',
        '                <span id="authenticated-user-info">',
        '                    {DevilryUser.username}',
        '                </span>',
        '                | <a class="loginout-link" href="{DevilrySettings.DEVILRY_LOGOUT_URL}">Log out</a>',
        '            </tpl>',
        '            <tpl if="!DevilryUser.is_authenticated">',
        '                <a class="loginout-link" href="{DevilrySettings.DEVILRY_LOGIN_URL}">Log in</a>',
        '            </tpl>',
        '        </div>',
        '    </div>',
        '    <div class="nav {navclass}">',
        '        <ul>',
        '            <li class="student-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/student/">Student</a></li>',
        '            <li class="examiner-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/examiner/">Examiner</a></li>',
        '            <li class="administrator-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/administrator/">Administrator</a></li>',
        '            <li class="externallink-navitem"><a href="{DevilrySettings.DEVILRY_HELP_URL}" target="_blank">Help</a></li>',
        '        </ul>',
        '    </div>',
        '</div>'
    ),

    config: {
        navclass: ''
    },

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
