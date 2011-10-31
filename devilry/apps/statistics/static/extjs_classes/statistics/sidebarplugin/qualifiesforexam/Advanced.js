Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                cls: 'readable-section',
                html: '<strong>Coming soon.</strong> If the other methods do not cover your needs, you can track our progress towards an advanced filter on <a href="https://github.com/devilry/devilry-django/issues/236">our issue tracker</a>.'
            }]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        return false;
    }
});
