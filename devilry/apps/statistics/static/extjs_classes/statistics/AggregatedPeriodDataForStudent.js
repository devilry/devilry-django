Ext.define('devilry.statistics.AggregatedPeriodDataForStudent', {
    
    constructor: function(config) {
        this.initConfig(config);

        this.labels = {};
        this.groupsByAssignmentId = {};
    }
});
