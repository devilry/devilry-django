Ext.define('devilry_student.model.OpenGroupDeadlineExpired', {
    extend: 'devilry_student.model.OpenGroup',

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/open-groups/',
        extraParams: {
            format: 'json',
            only: 'deadline_expired'
        },
        reader: {
            type: 'json'
        }
    }
});
