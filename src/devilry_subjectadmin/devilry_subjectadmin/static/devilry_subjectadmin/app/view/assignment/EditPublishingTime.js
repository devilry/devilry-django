/**
 * A window for editing the publishing time of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditPublishingTime', {
    extend: 'Ext.window.Window',
    alias: 'widget.editpublishingtime',
    cls: 'devilry_subjectadmin_editpublishingtime bootstrap',
    requires: [
        'devilry_extjsextras.SaveButton'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            width: 460,
            height: 290,
            closable: false,
            modal: true,
            title: gettext('Publishing time'),
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
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'box',
                    tpl: '<p>{help}</p>',
                    data: {
                        help: gettext('Choose a time when time when students will be able to start adding deliveries on the assignment. Note that students must be registered on the assignment as well before they can add any deliveries. ')
                    },
                    margin: '0 0 10 0'
                }, {
                    xtype: 'devilry_extjsextras-datetimefield',
                    name: 'publishing_time'
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
