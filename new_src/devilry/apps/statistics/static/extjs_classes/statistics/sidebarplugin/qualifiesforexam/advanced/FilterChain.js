Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterChain', {
    extend: 'Ext.data.Store',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter'
    ],

    config: {
        filterArgsArray: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.fields = ['filter'];
        this.callParent(arguments);
        if(this.filterArgsArray) {
            Ext.each(this.filterArgsArray, function(filterArgs, index) {
                this.addFilter(filterArgs);
            }, this);
        }
    },

    addFilter: function(filterConf) {
        this.add({
            filter: this.createFilter(filterConf)
        });
    },

    createFilter: function(filterConf) {
        return Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter', filterConf);
    },

    match: function(loader, studentRecord) {
        var matches = false;
        Ext.each(this.data.items, function(record, index) {
            var filter = record.get('filter');
            if(filter.match(studentRecord)) {
                matches = true;
                return false; // Break
            }
        }, this);
        return matches;
    },

    toExportArray: function() {
        var result = [];
        Ext.each(this.data.items, function(record, index) {
            var filter = record.get('filter');
            result.push(filter.toExportObject());
        }, this);
        return result;
    }
});
