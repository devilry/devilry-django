Ext.define('devilry.statistics.AggregatedPeriodDataForStudent', {

    config: {
        username: undefined,
        relatedstudent: undefined
    },
    
    constructor: function(config) {
        this.initConfig(config);

        this.labels = {};
        this.groupsByAssignmentId = {};
    }
});
