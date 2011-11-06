Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterChainEditor'
    ],

    initComponent: function() {
        this.filterchain = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain');
        this.filterchain.addFilter({
            pointspecArgs: {
                assignments: [[this.loader.findAssignmentByShortName('extra').get('id')]],
                min: 5,
                max: undefined
            },
            must_pass: [[this.loader.findAssignmentByShortName('week1').get('id')]]
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'statistics-filterchaineditor',
                filterchain: this.filterchain,
                assignment_store: this.loader.assignment_store,
                flex: 1,
                margin: {bottom: 10}
            }, this.defaultButtonPanel]
        });
        console.log(this.settings);

        this.callParent(arguments);
    },

    getSettings: function() {
        return this.filterchain.toExportArray();
    },

    filter: function(studentRecord) {
        return this.filterchain.match(this.loader, studentRecord);
    }
});
