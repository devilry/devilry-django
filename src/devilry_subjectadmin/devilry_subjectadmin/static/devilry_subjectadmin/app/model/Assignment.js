/** Assignment model. */
Ext.define('devilry_subjectadmin.model.Assignment', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedAssignment',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedassignment/',
        orderby: ['-publishing_time'],
        result_fieldgroups: ["subject", "period"]
    }),
});
