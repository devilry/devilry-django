/**
 * A window for editing the publishing time of an Assignment.
 * */
Ext.define('subjectadmin.view.assignment.EditPublishingTime', {
    extend: 'Ext.window.Window',
    alias: 'widget.editpublishingtime',
    cls: 'editpublishingtime',
    requires: [
        'themebase.SaveButton'
    ],

    /**
     * @cfg {subjectadmin.model.Assignment} assignmentRecord (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            width: 330,
            height: 270,
            modal: true,
            title: dtranslate('subjectadmin.assignment.editpublishingtime.title'),
            items: {
                xtype: 'form',
                bodyPadding: 20,
                autoScroll: true,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    html: dtranslate('subjectadmin.assignment.editpublishingtime.help'),
                    margin: {bottom: 20}
                }, {
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'themebase-datetimefield',
                    name: 'publishing_time',
                    margin: {top: 20},
                    //value: this.assignmentRecord.get('publishing_time')
                }],
                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'bottom',
                    ui: 'footer',
                    padding: 0,
                    items: ['->', {
                        xtype: 'savebutton',
                        formBind: true //only enabled once the form is valid
                    }]
                }]
            }
        });
        this.callParent(arguments);
    }
});
