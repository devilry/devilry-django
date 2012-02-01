Ext.define('subjectadmin.controller.ChoosePeriodTestMock', {
    extend: 'subjectadmin.controller.ChoosePeriod',

    views: [
        'chooseperiod.ActivePeriodsListTestMock',
        'chooseperiod.ChoosePeriod'
    ],

    stores: [
        'ActivePeriodsTestMock'
    ],

    getActivePeriodsStore: function() {
        return this.getActivePeriodsTestMockStore();
    },

    init: function() {
        var initialData = [{
            id: 0,
            parentnode__short_name:'duck1100',
            short_name:'2011h',
            start_time: '2011-01-01T12:00:00'
        }, {
            id: 1,
            parentnode__short_name:'duck1100',
            short_name:'2012h',
            start_time: '2012-01-03T12:30:00'
        }, {
            id: 2,
            parentnode__short_name:'duck-mek2030',
            short_name:'2012h',
            start_time: '2012-01-16T01:30:00'
        }];

        this.getActivePeriodsTestMockStore().proxy.setData(initialData);
        this.callParent();
    }
});
