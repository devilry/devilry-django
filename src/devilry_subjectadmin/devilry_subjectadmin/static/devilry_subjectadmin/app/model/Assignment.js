/** Assignment model. */
Ext.define('devilry_subjectadmin.model.Assignment', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedAssignment',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedassignment/',
        headers: {X_DEVILRY_USE_EXTJS: true},
        orderby: ['-publishing_time'],
        result_fieldgroups: ["subject", "period"]
    }),
});
