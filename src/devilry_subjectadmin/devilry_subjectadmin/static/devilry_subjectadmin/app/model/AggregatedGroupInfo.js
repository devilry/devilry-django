Ext.define('devilry_subjectadmin.model.AggregatedGroupInfo', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'deadlines', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/aggregated-groupinfo',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    has_any_deadlines: function() {
        var deadlines = this.get('deadlines');
        return deadlines.length > 0;
    },

    statics: {
        parseDateTime: function(datetimeString) {
            return Ext.Date.parse(datetimeString, 'Y-m-d H:i:s');
        }
    }
});
