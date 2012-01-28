Ext.define('subjectadmin.store.ActivePeriods', {
    extend: 'Ext.data.Store',
    model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedperiod/',
        result_fieldgroups: ["period", "subject"],
        //orderby: ['-start_time']
    })
});
