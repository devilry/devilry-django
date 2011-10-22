Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    constructor: function(config) {
        this.callParent([config]);
    },

    setLabel: function(label, value) {
        var labels = this.get('labels');
        labels[label] = value;
        this.set('labels', labels);
        this.set('labelKeys', Ext.Object.getKeys(labels));
    },

    delLabel: function(label) {
        var labels = this.get('labels');
        delete labels[label];
        this.set('labels', labels);
        this.set('labelKeys', Ext.Object.getKeys(labels));
    }
});
