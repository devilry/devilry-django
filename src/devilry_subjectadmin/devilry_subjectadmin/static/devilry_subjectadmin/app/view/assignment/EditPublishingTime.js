/**
 * A window for editing the publishing time of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditPublishingTime', {
    extend: 'Ext.window.Window',
    alias: 'widget.editpublishingtime',
    cls: 'editpublishingtime bootstrap',
    requires: [
        'themebase.SaveButton'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            width: 330,
            height: 270,
            closable: false,
            modal: true,
            title: dtranslate('devilry_subjectadmin.assignment.publishing_time.label'),
            items: {
                xtype: 'form',
                bodyPadding: 20,
                autoScroll: true,
                border: 0,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    html: dtranslate('devilry_subjectadmin.assignment.publishing_time.edithelp'),
                    margin: {bottom: 20}
                }, {
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'themebase-datetimefield',
                    name: 'publishing_time',
                    margin: {top: 20}
                }],
                buttons: ['->', {
                    xtype: 'cancelbutton'
                }, {
                    xtype: 'savebutton',
                    formBind: true //only enabled once the form is valid
                }]
            }
        });
        this.callParent(arguments);
    }
});
