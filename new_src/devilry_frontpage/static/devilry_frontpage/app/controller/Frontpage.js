Ext.define('devilry_frontpage.controller.Frontpage', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox',
        'devilry_authenticateduserinfo.UserInfo'
    ],

    views: [
        'FrontpageOverview'
    ],

    refs: [{
        ref: 'frontpage_overview',
        selector: 'viewport frontpage_overview'
    }, {
        ref: 'roles',
        selector: 'viewport frontpage_overview devilryheader_roles'
    }],

    init: function() {
        this.control({
            'viewport frontpage_overview devilryheader_roles': {
                render: this._onRenderRoles
            }
        });
    },

    _onRenderRoles: function() {
        devilry_authenticateduserinfo.UserInfo.load(function(userInfoRecord) {
            this.getRoles().setUserInfoRecord(userInfoRecord);
        }, this);
    }
});
