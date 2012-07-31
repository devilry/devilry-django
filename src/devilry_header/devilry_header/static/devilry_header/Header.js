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
        'devilry_header.UserButton',
        'devilry_header.HoverMenu',
        'devilry_header.Roles',
        'devilry_authenticateduserinfo.UserInfo'
    ],

    constructor: function() {
        devilry_authenticateduserinfo.UserInfo.load(); // Load the userinfo as soon as possible.
        this.callParent(arguments);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'box',
                width: 80,
                cls: 'devilrylogo',
                tpl: '<span class="logotext">{text}</span>',
                data: {
                    text: 'Devilry'
                }
            }, {
                xtype: 'devilryheader_currentrolebutton',
                //width: 100,
                listeners: {
                    scope: this,
                    render: this._onRender,
                    trigger: this._onTrigger
                }
            }, {
                xtype: 'container',
                itemId: 'breadcrumbarea',
                cls: 'breadcrumbarea',
                //style: 'background-color: #333 !important;',
                flex: 1,
            }, {
                xtype: 'container',
                width: 100,
                layout: 'fit',
                padding: 5,
                items: [{
                    xtype: 'devilryheader_userbutton',
                    text: gettext('Loading ...'),
                    listeners: {
                        scope: this,
                        toggle: this._onToggleUserButton
                    }
                }]
            }, {
                xtype: 'devilryheader_hovermenu',
                listeners: {
                    scope: this,
                    show: this._onShowHovermenu,
                    hide: this._onHideHovermenu
                }
            }]
        });
        this.callParent(arguments);
    },

    _getCurrentRoleButton: function() {
        return this.down('devilryheader_currentrolebutton');
    },
    _getHoverMenu: function() {
        return this.down('devilryheader_hovermenu');
    },
    _getUserButton: function() {
        return this.down('devilryheader_userbutton');
    },
    _getBreadcrumbArea: function() {
        return this.down('#breadcrumbarea');
    },

    setBreadcrumbComponent: function(config) {
        this._getBreadcrumbArea().removeAll();
        this._getBreadcrumbArea().add(config);
    },

    _onRender: function() {
        this._getCurrentRoleButton().setCurrentRole('Student', 'student');
        devilry_authenticateduserinfo.UserInfo.load(this._onLoadUserInfo, this);
    },

    _onLoadUserInfo: function(userInfoRecord) {
        this._getHoverMenu().setUserInfoRecord(userInfoRecord);
        this._getUserButton().setText(userInfoRecord.getDisplayName());
    },

    _onToggleUserButton: function(button) {
        var hovermenu = this._getHoverMenu();
        if(button.pressed) {
            hovermenu.show();
        } else {
            hovermenu.hide();
        }
    },

    _onTrigger: function() {
        //var hovermenu = this._getHoverMenu();
        //if(hovermenu.isVisible()) {
            //hovermenu.hide();
        //} else {
            //hovermenu.show();
        //}
        this._getUserButton().toggle();
    },

    _onShowHovermenu: function() {
        console.log('Show menu');
    },
    _onHideHovermenu: function() {
        console.log('Hide menu');
    },
});
