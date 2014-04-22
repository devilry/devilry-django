Ext.application({
    name: 'devilry_header',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header/app',
    paths: {
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo'
    },

    requires: [
        'Ext.layout.container.Column',
        'Ext.form.field.ComboBox',
        'Ext.layout.container.Border',
        'devilry_header.Header2',
        'devilry_header.Breadcrumbs'
    ],

    launch: function() {
        this._createHeader();
    },

    _createHeader:function () {
        this.breadcrumbs = Ext.widget('breadcrumbs', {
            defaultBreadcrumbs: [{
                text: gettext("Dashboard"),
                url: '#'
            }]
        });

        this.headercontainer = Ext.widget('devilryheader2', {
            // cls: 'devilry_subtlebg',
            navclass: 'subjectadmin',
            breadcrumbs: this.breadcrumbs,
            renderTo: 'devilryheader-container',
            cls: 'devilryheader-nonapp'
        });

        Ext.getBody().addCls('devilryheader-nonapp-bodyoffset');
    }
});
