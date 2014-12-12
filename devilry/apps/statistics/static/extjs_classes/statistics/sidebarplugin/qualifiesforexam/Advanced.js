Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterChainEditor'
    ],

    initComponent: function() {
        this.filterchain = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain', {
            filterArgsArray: this.settings? this.settings.filterArgsArray: undefined
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'box',
                cls: 'readable-section',
                html: Ext.String.format('Advanced filters have a dedicated guide in the Administrator section of the <a href="{0}" target="_blank">Help</a>.', DevilrySettings.DEVILRY_HELP_URL)
            }, {
                xtype: 'statistics-filterchaineditor',
                title: 'Rules',
                filterchain: this.filterchain,
                assignment_store: this.loader.assignment_store,
                flex: 1,
                margin: '10 0 10 0'
            }, this.defaultButtonPanel]
        });

        this.callParent(arguments);
    },

    getSettings: function() {
        return {
            filterArgsArray: this.filterchain.toExportArray()
        };
    },

    filter: function(studentRecord) {
        return this.filterchain.match(this.loader, studentRecord);
    }
});
