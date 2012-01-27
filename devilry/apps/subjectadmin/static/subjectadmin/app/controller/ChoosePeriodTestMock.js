Ext.define('subjectadmin.controller.ChoosePeriodTestMock', {
    extend: 'subjectadmin.controller.ChoosePeriod',

    views: [
        'NextButton',
        'chooseperiod.ActivePeriodsListTestMock',
        'chooseperiod.ChoosePeriod'
    ],

    stores: [
        'ActivePeriodsTestMock'
    ],

    getActivePeriodsStore: function() {
        return this.getActivePeriodsTestMockStore();
    }
});
