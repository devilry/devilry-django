Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    constructor: function(config) {
        this.labels = {};
        this.groupsByAssignmentId = {};
        this.callParent([config]);
    }
});
