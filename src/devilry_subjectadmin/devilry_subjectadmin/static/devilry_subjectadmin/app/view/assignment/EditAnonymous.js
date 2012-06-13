/**
 * A window for editing the anonymous attribute of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditAnonymous', {
    extend: 'Ext.window.Window',
    alias: 'widget.editanonymous',
    cls: 'editanonymous bootstrap',
    requires: [
        'devilry_extjsextras.SaveButton'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            width: 330,
            height: 270,
            closable: false,
            modal: true,
            title: dtranslate('devilry_subjectadmin.assignment.anonymous.label'),
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
                    html: dtranslate('devilry_subjectadmin.assignment.anonymous.help'),
                    margin: {bottom: 20}
                }, {
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'checkbox',
                    boxLabel: dtranslate('devilry_subjectadmin.assignment.anonymous.label'),
                    name: 'anonymous',
                    uncheckedValue: false,
                    inputValue: true,
                    margin: {top: 20}
                }],
                buttons: ['->', {
                    xtype: 'cancelbutton'
                }, {
                    xtype: 'savebutton'
                }]
            }
        });
        this.callParent(arguments);
    }
});
