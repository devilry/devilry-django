Ext.application({
    name: 'devilry_qualifiesforexam_select',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/devilry_qualifiesforexam_select/app',
    paths: {
        'devilry_extjsextras': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_extjsextras',
        'devilry_subjectadmin': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_subjectadmin/app',
        'devilry_theme': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_theme',
        'devilry_i18n': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_i18n',
        'devilry_authenticateduserinfo': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_authenticateduserinfo',
        'devilry_header': DevilrySettings.DEVILRY_STATIC_URL + '/devilry_header/app'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.layout.container.Border',
        'Ext.layout.container.Column',
        'Ext.form.field.ComboBox',
        'devilry_header.Header2',
        'devilry_extjsextras.FloatingAlertmessageList'
    ],

    controllers: [
        'SelectQualifiedStudentsController'
    ],

    refs: [{
        ref: 'alertmessagelist',
        selector: 'viewport floatingalertmessagelist#appAlertmessagelist'
    }],

    launch: function() {
        if(window.location.href.match(/^.+\/devilry_qualifiesforexam_select\/$/)) {
            this.viewport = Ext.create('Ext.container.Viewport', {
                xtype: 'box',
                html: 'ExtJS build view. Only used to help the ExtJS builder find all files needed to build the app.'
            });
        } else {
            this.viewport = Ext.create('Ext.container.Viewport', {
                xtype: 'container',
                layout: 'border',
                items: [{
                    xtype: 'devilryheader2',
                    region: 'north',
                    navclass: 'subjectadmin'
                }, {
                    xtype: 'container',
                    region: 'center',
                    cls: 'devilry_subtlebg',
                    layout: 'fit',
                    padding: 20,
                    items: [{
                        xtype: 'floatingalertmessagelist',
                        itemId: 'appAlertmessagelist'
                    }, {
                        xtype: 'selectqualifiedstudentsview'
                    }]
                    
                }]
            });
        }
    }
});
