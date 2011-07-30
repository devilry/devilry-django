Ext.define('devilry.extjshelpers.forms.Deadline', {
    extend: 'Ext.form.Panel',
    alias: 'widget.deadlineform',
    cls: 'widget-deadlineform',

    // Fields will be arranged vertically, stretched to full width
    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },

    defaultType: 'textfield',
    items: [{
        name: "text",
        fieldLabel: "text",
        xtype: 'textfield'
    }, {
        name: "deadline",
        fieldLabel: "deadline",
        xtype: 'datefield',
        format: 'Y-m-d H:i:s'
    }]
});
