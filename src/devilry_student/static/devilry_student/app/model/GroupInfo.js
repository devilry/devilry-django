Ext.define('devilry_student.model.GroupInfo', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'name', type: 'string'},
        {name: 'status', type: 'string'},
        {name: 'is_open', type: 'bool'},
        {name: 'deadline_handling', type: 'int'},
        {name: 'candidates', type: 'auto'},
        {name: 'examiners', type: 'auto'},
        {name: 'deadlines', type: 'auto'},
        {name: 'breadcrumbs', type: 'auto'},
        {name: 'add_delivery_url', type: 'string'},
        {name: 'delivery_types', type: 'int'},
        {name: 'active_feedback', type: 'auto'},
        {name: 'is_relatedstudent_on_period', type: 'auto'},
        {name: 'is_registrated', type: 'bool'},
        {name: 'students_can_create_groups_now', type: 'bool'}
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
        var hard_deadlines = this.get('deadline_handling') === 1;
        return this.deadline_expired() && hard_deadlines;
    },

    deadline_expired: function() {
        if(this.has_any_deadlines()) {
            return !this.get('deadlines')[0].in_the_future;
        } else {
            return false;
        }
    },

    has_any_deadlines: function() {
        var deadlines = this.get('deadlines');
        return deadlines.length > 0;
    },

    can_add_deliveries: function() {
        if(!this.get('is_open')) {
            return false;
        }
        if(!this.has_any_deadlines()) {
            return false;
        }
        if(this.get('delivery_types') == 1) { // 1 == NON_ELECTRONIC
            return false;
        }
        var hard_deadlines = this.get('deadline_handling') === 1;
        if(hard_deadlines) {
            return this.get('deadlines')[0].in_the_future;
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
