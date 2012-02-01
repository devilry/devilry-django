Ext.define('subjectadmin.model.PeriodTestMock', {
    extend: 'subjectadmin.model.Period',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'simplifiedperiodproxy'
    }
});
