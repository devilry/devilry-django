/** Period model. */
Ext.define('devilry_subjectadmin.model.Period', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedPeriod',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedperiod/',
        orderby: ['-start_time'],
        result_fieldgroups: ["subject"],
    }),
});
