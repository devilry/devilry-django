Ext.define('devilry_student.model.GroupInfo', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'name', type: 'string'},
        {name: 'is_open', type: 'bool'},
        {name: 'candidates', type: 'auto'},
        {name: 'examiners', type: 'auto'},
        {name: 'deadlines', type: 'auto'},
        {name: 'breadcrumbs', type: 'auto'},
        {name: 'add_delivery_url', type: 'string'},
        {name: 'active_feedback', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/aggregated-groupinfo',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    statics: {
        parseDateTime: function(datetimeString) {
            return Ext.Date.parse(datetimeString, 'Y-m-d H:i:s');
        }
    }
});
