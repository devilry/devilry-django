/**
 * Devilry page header.
 */
Ext.define('devilry_header.Header', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader',
    margin: '0 0 0 0',
    height: 30, // NOTE: Make sure to adjust $headerHeight in the stylesheet if this is changed

    requires: [
        'devilry_header.FlatButton',
        'devilry_header.HoverMenu',
        'devilry_header.SearchMenu',
        'devilry_header.Roles',
        'devilry_authenticateduserinfo.UserInfo',
        'devilry_header.Breadcrumbs'
    ],


    navclass_to_rolename: {
        'no_role': gettext('Select role'),
        'student': gettext('Student'),
        'examiner': gettext('Examiner'),
        'subjectadmin': interpolate(gettext('%(Subject_term)s administrator'), {
            Subject_term: gettext('Subject')
        }, true),
        'nodeadmin': interpolate(gettext('%(Node_term)s administrator'), {
            Node_term: gettext('Node')
        }, true),
        'superuser': gettext('Superuser')
    },

    navclass_to_dashboard_url: {
        'student': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/#',
        'examiner': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/examiner/',
        'administrator': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/',
        'superuser': DevilrySettings.DEVILRY_URLPATH_PREFIX + '/superuser/'
    },

    /**
     * @cfg {string} [navclass]
     * The css class to style the header buttons with.
     */

    /**
     * @cfg {Object} [breadcrumbs=devilry_header.Breadcrumbs]
     * The object to use for breadcrumbs. You can also set this after load with #setBreadcrumbComponent.
     * Defaults to an instance of devilry_header.Breadcrumbs.
     */

    constructor: function(config) {
        console.warn('Rendering the OLD header (devilry_header.Header).');
        if(Ext.isEmpty(config.cls)) {
            config.cls = 'devilryheader';
        } else {
            config.cls = ['devilryheader', config.cls].join(' ');
        }
        if(!this.navclass_to_rolename[config.navclass]) {
            throw "Invalid navclass: " + config.navclass;
        }
        devilry_authenticateduserinfo.UserInfo.load(); // Load the userinfo as soon as possible.
        this.callParent(arguments);
    },

    initComponent: function() {
        var breadcrumbareaItem;
        if(this.breadcrumbs) {
            breadcrumbareaItem = this.breadcrumbs;
        } else {
            breadcrumbareaItem = Ext.widget('breadcrumbs');
        }
        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'box',
                //width: 110,
                cls: 'devilrylogo',
                tpl: '<a class="logotext" href="{frontpageurl}">{text}</a>',
                data: {
                    text: 'Devilry',
                    frontpageurl: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/'
                }
            }, {
                xtype: 'devilryheader_flatbutton',
                itemId: 'currentRoleButton',
                cls: 'flatbutton currentrolebutton',
                listeners: {
                    scope: this,
                    render: this._onRenderCurrentRoleButton,
                    click: this._onClickCurrentRoleButton
                }
            }, {
                xtype: 'container',
                itemId: 'breadcrumbarea',
                cls: 'breadcrumbarea',
                items: [breadcrumbareaItem],
                flex: 1
            }, {
                xtype: 'devilryheader_flatbutton',
                itemId: 'searchButton',
                enableToggle: true,
                width: 50,
                tpl: [
                    '<div class="textwrapper bootstrap">',
                    '<i class="icon-search icon-white"></i>',
                    '</div>'
                ],
                data: {},
                listeners: {
                    scope: this,
                    render: this._onRenderSearchButton,
                    toggle: this._onToggleSearchButton
                }
            }, {
                xtype: 'devilryheader_flatbutton',
                itemId: 'userButton',
                enableToggle: true,
                width: 100,
                listeners: {
                    scope: this,
                    render: this._onRenderUserButton,
                    toggle: this._onToggleUserButton
                }
            }, {
                // NOTE: This component is floating, so it is not really part of the layout
                xtype: 'devilryheader_searchmenu',
                listeners: {
                    scope: this,
                    show: this._onShowSearchmenu,
                    hide: this._onHideSearchmenu
                }
            }, {
                // NOTE: This component is floating, so it is not really part of the layout
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
        return this.down('#currentRoleButton');
    },
    _getHoverMenu: function() {
        return this.down('devilryheader_hovermenu');
    },
    _getUserButton: function() {
        return this.down('#userButton');
    },
    _getSearchButton: function() {
        return this.down('#searchButton');
    },
    _getSearchMenu: function() {
        return this.down('devilryheader_searchmenu');
    },
    _getBreadcrumbArea: function() {
        return this.down('#breadcrumbarea');
    },

    setNavClass: function(navclass) {
        this.navclass = navclass;
        this._updateRoleButton();
        this._getUserButton().addExtraClass(this.navclass);
    },


    setBreadcrumbComponent: function(config) {
        this._getBreadcrumbArea().removeAll();
        this._getBreadcrumbArea().add(config);
    },

    _updateRoleButton: function() {
        this._getCurrentRoleButton().setText(this.navclass_to_rolename[this.navclass]);
        this._getCurrentRoleButton().addExtraClass(this.navclass);
    },
    _onRenderCurrentRoleButton: function() {
        this._updateRoleButton();
    },
    _onRenderUserButton: function() {
        devilry_authenticateduserinfo.UserInfo.load(function(userInfoRecord) {
            this._getHoverMenu().setUserInfoRecord(userInfoRecord);
            this._getUserButton().addExtraClass(this.navclass);
            this._getUserButton().setText(userInfoRecord.getDisplayName());
        }, this);
    },

    _onClickCurrentRoleButton: function() {
        this._getUserButton().toggle();
    },

    _onToggleUserButton: function(button) {
        var hovermenu = this._getHoverMenu();
        if(button.pressed) {
            hovermenu.show();
        } else {
            hovermenu.hide();
        }
    },

    _onShowHovermenu: function() {
        this._getSearchButton().setPressedWithEvent(false); // Hide search menu when showing hover menu
        this._getCurrentRoleButton().setPressedCls();
        this._getUserButton().setPressedCls();
    },
    _onHideHovermenu: function() {
        this._getCurrentRoleButton().setNotPressedCls();
        this._getUserButton().setNotPressedCls();
    },


    _onRenderSearchButton:function () {
        this._getSearchButton().addExtraClass('devilry_header_search_button');
    },

    _onToggleSearchButton: function(button) {
        var searchmenu = this._getSearchMenu();
        if(button.pressed) {
            searchmenu.show();
        } else {
            searchmenu.hide();
        }
    },

    _onShowSearchmenu: function() {
        this._getUserButton().setPressedWithEvent(false); // Hide hover menu when showing search menu
        this._getSearchButton().setPressedCls();
    },
    _onHideSearchmenu: function() {
        this._getSearchButton().setPressed(false);
    }
});
