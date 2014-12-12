Ext.define('devilry_qualifiesforexam.utils.Breadcrumbs', {
    extend: 'devilry_subjectadmin.utils.Breadcrumbs',

    formatUrl: function (url, meta) {
        if(!Ext.isEmpty(meta) && meta.applocal) {
            return url;
        } else if(url.match(/^#.*/)) {
            // All breadcrumbs not marked as applocal are assumed to lead to devilry_subjectadmin.
            return Ext.String.format('{0}/devilry_subjectadmin/{1}',
                DevilrySettings.DEVILRY_URLPATH_PREFIX, url);
        } else {
            return url;
        }
    }
});
