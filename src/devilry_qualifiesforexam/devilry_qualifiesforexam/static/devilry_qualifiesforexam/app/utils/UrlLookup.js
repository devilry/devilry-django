Ext.define('devilry_qualifiesforexam.utils.UrlLookup', {
    singleton: true,

    selectplugin: function(period_id) {
        return Ext.String.format('#/{0}/selectplugin', period_id);
    }
});
