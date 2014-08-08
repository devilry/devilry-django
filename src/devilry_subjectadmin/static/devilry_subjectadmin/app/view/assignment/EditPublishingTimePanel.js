/**
 * A panel for editing the publishing time of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditPublishingTimePanel', {
    extend: 'devilry_extjsextras.OkCancelPanel',
    alias: 'widget.editpublishingtimepanel',
    cls: 'devilry_subjectadmin_editpublishingtimepanel bootstrap',

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
                        help: gettext('Choose a time when students will be able to start adding deliveries on the assignment. Note that students must be registered on the assignment as well before they can add any deliveries.')
                    },
                    margin: '0 0 10 0'
                }, {
                    xtype: 'devilry_extjsextras-datetimefield',
                    name: 'publishing_time'
                }]
            }
        });
        this.callParent(arguments);
    }
});
