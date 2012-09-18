/**
 * A panel for editing the first deadline of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditFirstDeadlinePanel', {
    extend: 'devilry_extjsextras.OkCancelPanel',
    alias: 'widget.editfirstdeadlinepanel',
    cls: 'devilry_subjectadmin_editfirstdeadlinepanel bootstrap',

    requires: [
        'devilry_extjsextras.form.DateTimeField'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            oktext: gettext('Save'),
            items: {
                xtype: 'form',
                bodyPadding: 10,
                autoScroll: true,
                border: 0,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'box',
                    tpl: '<p>{help}</p>',
                    data: {
                        help: gettext('Select the default deadline that will be added to groups when you add them to this assignment. Changing this does not affect existing groups.')
                    },
                    margin: '0 0 10 0'
                }, {
                    xtype: 'devilry_extjsextras-datetimefield',
                    name: 'first_deadline'
                }]
            }
        });
        this.callParent(arguments);
    }
});
