/** Subject model. */
Ext.define('devilry_subjectadmin.model.Subject', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedSubject',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedsubject/',
        result_fieldgroups: []
    }),
});
