Ext.define('devilry_subjectadmin.view.assignment.GradeEditorSelectWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradeeditorselectwindow',
    cls: 'devilry_subjectadmin_gradeeditorselect bootstrap',
    requires: [
        'devilry_extjsextras.SaveButton',
        'devilry.gradeeditors.GradeEditorSelector'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            width: 500,
            height: 300,
            closable: false,
            modal: true,
            title: gettext('Select grade editor'),
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
                    name: 'gradeeditorid',
                    fieldLabel: gettext("Select a grade editor"),
                    xtype: 'gradeeditorselector'
                }, {
                    xtype: 'box',
                    tpl: '<p>{help}</p>',
                    data: {
                        help: 'HELP HERE'
                    },
                    margin: '0 0 10 0'
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
