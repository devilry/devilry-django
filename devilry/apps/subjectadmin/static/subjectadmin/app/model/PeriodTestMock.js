/** Test mockup model for Period. */
Ext.define('subjectadmin.model.PeriodTestMock', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'simplifiedperiodproxy',

        validator: function(operation) {
        }
    }
});
