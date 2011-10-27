Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.None', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',
    pluginname: 'none',

    initComponent: function() {
        Ext.apply(this, {
            items: [this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        return false;
    }
});
