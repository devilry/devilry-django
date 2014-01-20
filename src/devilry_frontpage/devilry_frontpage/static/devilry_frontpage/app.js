Ext.application({
    name: 'devilry_frontpage',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_frontpage/app',
    paths: {
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header/app',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.layout.container.Border',
        'Ext.resizer.Splitter',
        'Ext.resizer.SplitterTracker',
        'Ext.resizer.BorderSplitterTracker',

        'Ext.form.field.ComboBox',
        'Ext.form.field.Picker',
        'Ext.form.field.Trigger',
        'Ext.layout.component.field.Trigger',
        'Ext.view.View',
        'Ext.selection.DataViewModel',
        'Ext.selection.Model',
        'Ext.layout.component.BoundList',
        'Ext.toolbar.Paging',
        'Ext.toolbar.TextItem',
        'Ext.form.field.Number',
        'Ext.layout.container.Column',

        'devilry_extjsextras.Router',
        'devilry_extjsextras.RouteNotFound',
        'devilry_header.Header2',
        'devilry_header.Breadcrumbs'
    ],

    controllers: [
        'Frontpage'
    ],

    launch: function() {
        this._createViewport();
    },

    _createViewport: function() {
        this.viewport = Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [{
                xtype: 'devilryheader2',
                region: 'north',
                navclass: 'no_role'
            }, {
                xtype: 'frontpage_overview',
                region: 'center'
            }]
        });
    }
});
