Ext.define('subjectadmin.controller.period.OverviewTestMock', {
    extend: 'subjectadmin.controller.period.Overview',

    stores: [
        'PeriodsTestMock'
    ],

    getPeriodsStore: function() {
        return this.getPeriodsTestMockStore();
    }
});
