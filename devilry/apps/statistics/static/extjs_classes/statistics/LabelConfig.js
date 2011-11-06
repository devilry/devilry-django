Ext.define('devilry.statistics.LabelConfig', {
    config: {
        label: undefined
    },
    requires: [
        'devilry.statistics.Filter',
        'devilry.statistics.PointSpec'
    ],

    constructor: function(config) {
        this.filters = [];
        this.initConfig(config);
    },

    addFilter: function(filterConf) {
        this.filters.push(Ext.create('devilry.statistics.Filter', filterConf));
    },

    match: function(loader, studentRecord) {
        var matches = false;
        Ext.each(this.filters, function(filter, index) {
            if(filter.match(studentRecord)) {
                matches = true;
                return false; // Break
            }
        }, this);
        return matches;
    }
});
