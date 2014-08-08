/** Period model. */
Ext.define('devilry_subjectadmin.model.Period', {
    extend: 'Ext.data.Model',
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'auto'},
        {name: 'parentnode', type: 'auto'},
        {name: 'short_name',  type: 'string'},
        {name: 'long_name',  type: 'string'},
        {name: 'can_delete',  type: 'bool', persist:false},
        {name: 'etag',  type: 'string', persist:false},
        {name: 'admins',  type: 'auto'},
        {name: 'inherited_admins',  type: 'auto', persist:false},
        {name: 'start_time',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'end_time',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'breadcrumb',  type: 'auto', persist:false},
        {name: 'number_of_relatedexaminers',  type: 'int', persist:false},
        {name: 'number_of_relatedstudents',  type: 'int', persist:false}
    ],

    formatStartTime: function() {
        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(this.get('start_time'));
    },
    formatEndTime: function() {
        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(this.get('end_time'));
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
