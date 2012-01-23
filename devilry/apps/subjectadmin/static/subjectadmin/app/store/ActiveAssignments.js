Ext.define('subjectadmin.store.ActiveAssignments', {
    extend: 'Ext.data.Store',
    model: 'devilry.apps.administrator.simplified.SimplifiedAssignment',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedassignment/',
        result_fieldgroups: ["period", "subject"]
    })
});
