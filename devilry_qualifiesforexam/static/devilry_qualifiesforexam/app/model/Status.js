Ext.define('devilry_qualifiesforexam.model.Status', {
    extend: 'Ext.data.Model',
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int', pesist: false},
        {name: 'is_active', type: 'bool', pesist: false},
        {name: 'short_name', type: 'string', pesist: false},
        {name: 'long_name', type: 'string', pesist: false},
        {name: 'subject', type: 'auto', pesist: false},
        {name: 'active_status', type: 'auto', pesist: false},
        {name: 'statuses', type: 'auto', pesist: false},
        {name: 'perioddata', type: 'auto', pesist: false}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/status/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    getActiveStatus: function () {
        if(!Ext.isEmpty(this.get('active_status'))) {
            return this.get('active_status');
        } else if(!Ext.isEmpty(this.get('statuses'))) {
            return this.get('statuses')[0];
        } else {
            return null;
        }
    },

    formatCreatetime: function (createtime) {
        var dateobj = devilry_extjsextras.DatetimeHelpers.parseRestformattedDatetime(createtime);
        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dateobj);
    }
});
