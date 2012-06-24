Ext.define('devilry_subjectadmin.utils.UrlLookup', {
    singleton: true,

    subjectOverview: function(subject_id) {
        return Ext.String.format('/subject/{0}/', subject_id);
    },

    periodOverview: function(period_id) {
        return Ext.String.format('/period/{0}/', subject_id);
    },

    overviewByType: function(type, id) {
        var lowertype = type.toLowerCase();
        if(lowertype === 'period') {
            return this.periodOverview(id);
        } else if(lowertype === 'subject') {
            return this.subjectOverview(id);
        } else {
            Ext.Error.raise({
                msg: 'The given type does not have an overview',
                type: type,
                id: id
            });
        }
    }
});
