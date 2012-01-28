Ext.define('subjectadmin.controller.ChoosePeriodTestMock', {
    extend: 'subjectadmin.controller.ChoosePeriod',

    views: [
        'themebase.NextButton',
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
