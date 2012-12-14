Ext.define('devilry_subjectadmin.model.DeadlineBulk', {
    extend: 'Ext.data.Model',

    requires: [
        'Ext.Date',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    idProperty: 'bulkdeadline_id',
    fields: [
        {name: 'bulkdeadline_id', type: 'string'},
        {name: 'createmode', type: 'string'},
        {name: 'deadline',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'in_the_future',  type: 'bool', persist: false},
        {name: 'offset_from_now',  type: 'auto', persist: false},
        {name: 'text',  type: 'string'},
        {name: 'group_ids',  type: 'auto', defaultValue: null},
        {name: 'url',  type: 'string', persist: false},
        {name: 'groups',  type: 'auto', persist: false}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/deadlinesbulk/{0}/',
        url: null, // We use urlpatt to dynamically generate the url
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        },

        setUrl: function(assignment_id) {
            this.url = Ext.String.format(this.urlpatt, assignment_id);
        }
    },

    formatOffsetFromNow: function() {
        return devilry_extjsextras.DatetimeHelpers.formatTimedeltaRelative(
            this.get('offset_from_now'), this.get('in_the_future'));
    },

    formatTextOneline: function() {
        var maxlength = 50;
        var text = this.get('text');
        if(text === null || text.length === 0) {
            return null;
        }
        text = text.replace(/(\r\n|\n|\r)/gm, " ");
        return Ext.String.ellipsis(text, maxlength);
    },

    formatDeadline: function() {
        return devilry_extjsextras.DatetimeHelpers.formatDateTimeLong(this.get('deadline'));
    },

    updateBulkDeadlineIdFromOperation: function(operation) {
        var responseData = Ext.JSON.decode(operation.response.responseText);
        var bulkdeadline_id = responseData.bulkdeadline_id;
        this.set('bulkdeadline_id', bulkdeadline_id);
    },


    statics: {
        parseDateTime: function(datetimeString) {
            return Ext.Date.parse(datetimeString, 'Y-m-d H:i:s');
        }
    }
});
