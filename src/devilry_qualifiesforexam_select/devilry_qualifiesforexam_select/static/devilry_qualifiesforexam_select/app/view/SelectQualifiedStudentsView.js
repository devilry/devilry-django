Ext.define('devilry_qualifiesforexam_select.view.SelectQualifiedStudentsView', {
    extend: 'Ext.form.Panel',
    alias: 'widget.selectqualifiedstudentsview',

    requires: [
        'devilry_extjsextras.PrimaryButton',
        'devilry_qualifiesforexam_select.view.SelectQualifiedStudentsGrid'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            border: false,
            frame: false,
            items: [{
                xtype: 'selectqualifiedstudentsgrid'
            }],
            buttons: ['->', {
                xtype: 'button',
                scale: 'large',
                itemId: 'backButton',
                text: gettext('Back')
            }, {
                xtype: 'primarybutton',
                scale: 'large',
                itemId: 'nextButton',
                text: gettext('Next')
            }]
        });
        this.callParent(arguments);
    }
});
