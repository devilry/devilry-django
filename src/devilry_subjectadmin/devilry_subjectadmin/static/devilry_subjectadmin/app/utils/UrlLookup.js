Ext.define('devilry_subjectadmin.utils.UrlLookup', {
    statics: {
        subjectOverview: function(subject_id) {
            return Ext.String.format('/subject/{0}/', subject_id);
        }
    }
});
