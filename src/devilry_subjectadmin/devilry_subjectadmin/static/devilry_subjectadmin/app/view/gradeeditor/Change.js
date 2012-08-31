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
                xtype: 'gradeeditorchoosegrid',
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
                        xtype: 'savebutton'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
