Ext.define('devilry_subjectadmin.view.period.EditDurationPanel', {
    extend: 'devilry_extjsextras.OkCancelPanel',
    alias: 'widget.editperiod_duration',
    cls: 'devilry_subjectadmin_editdurationpanel bootstrap',

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
                border: false,
                layout: 'anchor',
                defaults: {
                    anchor: '100%',
                    labelAlign: 'top',
                    labelStyle: 'font-weight: bold'
                },
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    //xtype: 'box',
                    //tpl: '<p>{help}</p>',
                    //data: {
                    //},
                    //margin: '0 0 10 0'
                //}, {
                    xtype: 'devilry_extjsextras-datetimefield',
                    fieldLabel: gettext('Start time'),
                    cls: 'start_time_field',
                    name: 'start_time'
                }, {
                    xtype: 'devilry_extjsextras-datetimefield',
                    fieldLabel: gettext('End time'),
                    cls: 'end_time_field',
                    name: 'end_time'
                }]
            }
        });
        this.callParent(arguments);
    }
});
