Ext.define('devilry_subjectadmin.view.gradeeditor.Change' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.gradeeditorchange',
    cls: 'devilry_subjectadmin_gradeeditorchange',

    requires: [
        'devilry_subjectadmin.view.gradeeditor.ChooseGradeEditorGrid',
        'devilry_extjsextras.SaveButton'
    ],

    border: false,
    frame: false,

    initComponent: function() {
        Ext.apply(this, {
            layout: 'column',
            items: [{
                xtype: 'box',
                width: 300,
                cls: 'bootstrap',
                html: [
                    '<h2>', gettext('Select a grade editor'), '</h2>'
                ].join('')
            }, {
                columnWidth: 1, // Fill rest of the width
                xtype: 'container',
                layout: 'anchor',
                items: [{
                    xtype: 'gradeeditorchoosegrid',
                    anchor: '100%',
                }, {
                    xtype: 'container',
                    anchor: '100%',
                    cls: 'bootstrap',
                    layout: 'fit',
                    itemId: 'clearConfigConfirmContainer',
                    hidden: true,
                    items: {
                        xtype: 'container',
                        cls: 'alert alert-warning',
                        layout: 'anchor',
                        margin: '10 0 10 0',
                        items: [{
                            xtype: 'box',
                            anchor: '100%',
                            tpl: '<p>{text}</p>',
                            data: {
                                text: gettext('If you change grade editor your current configuration will be lost.')
                            }
                        }, {
                            xtype: 'checkbox',
                            anchor: '100%',
                            itemId: 'clearConfigConfirmCheckbox',
                            boxLabel: gettext('I want to change grade editor and clear my current configuration.')
                        }]
                    }
                }]
            }],
            dockedItems: [{
                dock: 'bottom',
                xtype: 'toolbar',
                margin: '5 0 10 0', // Leave a bit of space below the save-button
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    text: 'Cancel',
                    itemId: 'cancelButton'
                }, {
                    enabled: false,
                    xtype: 'savebutton'
                }]
            }]
            
        });
        this.callParent(arguments);
    }
});
