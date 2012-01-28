Ext.define('subjectadmin.store.ActiveAssignments', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Assignment',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedassignment/',
        result_fieldgroups: ["period", "subject"],
        orderby: ['-publishing_time']
    })
});
