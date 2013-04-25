Ext.define('devilry_qualifiesforexam.utils.UrlLookup', {
    singleton: true,

    selectplugin: function(period_id) {
        return Ext.String.format('#/{0}/selectplugin', period_id);
    },

    showstatus: function(period_id) {
        return Ext.String.format('#/{0}/showstatus', period_id);
    },

    showstatus_print: function(status_id) {
        return Ext.String.format('{0}/devilry_qualifiesforexam/statusprint/{1}',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX, status_id);
    }
});
