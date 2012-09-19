/**
 * A panel for editing the anonymous attribute of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditAnonymousPanel', {
    extend: 'devilry_extjsextras.OkCancelPanel',
    alias: 'widget.editanonymouspanel',
    cls: 'devilry_subjectadmin_editanonymouspanel bootstrap',

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            oktext: gettext('Save'),
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
                    //xtype: 'box',
                    //html: [
                        //'<p>', 
                        //'</p>',
                    //].join(''),
                    //margin: '0 0 10 0'
                //}, {
                    xtype: 'checkbox',
                    boxLabel: gettext('Anonymous'),
                    name: 'anonymous',
                    uncheckedValue: false,
                    inputValue: true
                }]
            }
        });
        this.callParent(arguments);
    }
});
