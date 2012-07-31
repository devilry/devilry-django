Ext.define('devilry_header.UserButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.devilryheader_userbutton',

    initComponent: function() {
        Ext.apply(this, {
            menu: [],
            enableToggle: true
        });
        this.callParent(arguments);
    }
});
