Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterEditor',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChainEditor'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [this.defaultButtonPanel]
        });
        console.log(this.settings);

        this.labelConfig = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain');
        this.labelConfig.addFilter({
            pointspecArgs: {
                assignments: [[this.loader.findAssignmentByShortName('extra').get('id')]],
                min: 5,
                max: undefined
            },
            must_pass: [[this.loader.findAssignmentByShortName('week1').get('id')]]
        });

        this.callParent(arguments);
    },

    getSettings: function() {
        return this.labelConfig.toExportArray();
    },

    filter: function(studentRecord) {
        return this.labelConfig.match(this.loader, studentRecord);
    }
});
