Ext.define('devilry_student.model.GroupInfo', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'name', type: 'string'},
        {name: 'is_open', type: 'bool'},
        {name: 'deadline_handling', type: 'int'},
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

    hard_deadline_expired: function() {
        var deadlines = this.get('deadlines');
        if(deadlines.length === 0) {
            return false;
        }
        var hard_deadlines = this.get('deadline_handling') === 1;
        return hard_deadlines && !deadlines[0].in_the_future;
    },

    can_add_deliveries: function() {
        if(!this.get('is_open')) {
            return false;
        }
        var deadlines = this.get('deadlines');
        if(deadlines.length === 0) {
            return false;
        }
        var hard_deadlines = this.get('deadline_handling') === 1;
        if(hard_deadlines) {
            return deadlines[0].in_the_future;
        } else {
            return true;
        }
    },

    statics: {
        parseDateTime: function(datetimeString) {
            return Ext.Date.parse(datetimeString, 'Y-m-d H:i:s');
        }
    }
});
