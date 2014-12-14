/** Used when managestudents need to search for groups without affecting the
 * grids that are using the Groups store. */
Ext.define('devilry_subjectadmin.store.SearchForGroups', {
    extend: 'devilry_subjectadmin.store.Groups',
    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/group/{0}/',
        url: null, // We use urlpatt to dynamically generate the url
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
