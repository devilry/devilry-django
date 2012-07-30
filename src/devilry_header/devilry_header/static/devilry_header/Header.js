/**
 * Devilry page header with the role tabs and log in/out links.
 */
Ext.define('devilry_header.Header', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader',
    cls: 'devilryheader',
    margins: '0 0 0 0',
    height: 30,

    requires: [
        'devilry_header.CurrentRoleButton',
        'devilry_header.Roles'
    ],

    /**
     * @cfg {string} navclass (required)
     */

    bodyTpl: [
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
                    '<li class="student-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/student/">',
                        pgettext('devilryheader', 'Student'),
                    '</a></li>',
                    '<li class="examiner-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/examiner/">',
                        pgettext('devilryheader', 'Examiner'),
                    '</a></li>',
                    '<li class="subjectadmin-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/devilry_subjectadmin/#">',
                        pgettext('devilryheader', 'Subjectadmin'),
                    '</a></li>',
                    '<li class="oldadmin-navitem"><a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/administrator/">',
                        'Administrator (old UI)',
                    '</a></li>',
                    '<li class="externallink-navitem"><a href="{DevilrySettings.DEVILRY_HELP_URL}" target="_blank">',
                        pgettext('devilryheader', 'Help'),
                    '</a></li>',
                '</ul>',
            '</div>',
        '</div>'
    ],

    //constructor: function(config) {
        //this.initConfig(config);
        //this.callParent([config]);
    //},

    initComponent: function() {
        //var data = {
            //navclass: this.navclass,
            //DevilrySettings: DevilrySettings,
            //DevilryUser: DevilryUser
        //};
        Ext.apply(this, {
            layout: 'border',
            items: [{
                xtype: 'devilryheader_currentrolebutton',
                region: 'west',
                width: 150,
                listeners: {
                    scope: this,
                    render: this._onRender,
                    trigger: this._onTrigger
                }
            }, this.breadcrumbarea = Ext.widget('container', {
                cls: 'breadcrumbarea',
                region: 'center'
            })]
        });
        this.callParent(arguments);
    },

    _getCurrentRoleButton: function() {
        return this.down('devilryheader_currentrolebutton');
    },

    setBreadcrumbComponent: function(config) {
        this.breadcrumbarea.removeAll();
        this.breadcrumbarea.add(config);
    },

    _onRender: function() {
        this._getCurrentRoleButton().setCurrentRole('Student', 'student');
    },

    _onTrigger: function() {
        console.log('trigger2');
    }
});
