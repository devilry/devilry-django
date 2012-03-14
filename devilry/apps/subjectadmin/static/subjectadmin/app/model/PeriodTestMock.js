/** Test mockup model for Period. */
Ext.define('subjectadmin.model.PeriodTestMock', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'periodproxy',

        validator: function(operation) {
        }
    }
});
