/** Period model. */
Ext.define('devilry_subjectadmin.model.Period', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'auto'},
        {name: 'parentnode', type: 'auto'},
        {name: 'short_name',  type: 'string'},
        {name: 'long_name',  type: 'string'},
        {name: 'can_delete',  type: 'bool'},
        {name: 'etag',  type: 'string'},
        {name: 'admins',  type: 'auto'},
        {name: 'inherited_admins',  type: 'auto'},
        {name: 'start_time',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'end_time',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'breadcrumb',  type: 'auto'},
        {name: 'number_of_relatedexaminers',  type: 'int'},
        {name: 'number_of_relatedstudents',  type: 'int'}
    ],

    formatStartTime: function() {
        return Ext.Date.format(this.get('start_time'), 'Y-m-d H:i');
    },
    formatEndTime: function() {
        return Ext.Date.format(this.get('end_time'), 'Y-m-d H:i');
    },

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/period/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
