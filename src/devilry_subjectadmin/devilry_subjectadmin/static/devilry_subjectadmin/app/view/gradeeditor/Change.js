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
            margin: '20 0 0 0',
            layout: 'column',
            items: [{
                xtype: 'box',
                width: 300,
                cls: 'bootstrap',
                padding: '0 20 0 0',
                html: [
                    '<h2>', gettext('Select a grade editor'), '</h2>',
                    '<p class="muted">',
                        gettext('Please select a grade editor. If your selected grade editor requires configuration, you will be able to do so after saving your choice.'),
                    '</p>'
                ].join('')
            }, {
                columnWidth: 1, // Fill rest of the width
                xtype: 'container',
                layout: 'anchor',
                margin: '10 0 0 0', // Align it better with the top of the "Select a grade editor" title.
                items: [{
                    xtype: 'gradeeditorchoosegrid',
                    anchor: '100%',
                }, {
                    xtype: 'container',
                    anchor: '100%',
                    cls: 'bootstrap clear_config_confirm',
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
                    cls: 'cancel_gradeeditor_change_button',
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
