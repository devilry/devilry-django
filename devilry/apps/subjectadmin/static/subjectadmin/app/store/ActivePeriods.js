Ext.define('subjectadmin.store.ActivePeriods', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Period',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedperiod/',
        result_fieldgroups: ["period", "subject"],
        //orderby: ['-start_time']
    })
});
