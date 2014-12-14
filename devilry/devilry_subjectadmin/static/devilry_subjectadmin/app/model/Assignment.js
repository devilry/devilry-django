/** Assignment model. */
Ext.define('devilry_subjectadmin.model.Assignment', {
    extend: 'Ext.data.Model',

    requires: [
        'Ext.Date',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    idProperty: 'id',
    fields: [
        {name: 'admins',  type: 'auto'},
        {name: 'breadcrumb',  type: 'auto'},
        {name: 'can_delete',  type: 'bool'},
        {name: 'anonymous',  type: 'bool'},
        {name: 'etag',  type: 'string'},
        {name: 'first_deadline',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'id', type: 'auto'},
        {name: 'inherited_admins',  type: 'auto'},
        {name: 'long_name',  type: 'string'},
        {name: 'parentnode', type: 'auto'},
        {name: 'publishing_time',  type: 'date', "dateFormat": "Y-m-d H:i:s"},
        {name: 'is_published',  type: 'bool', persist: false},
        {name: 'publishing_time_offset_from_now',  type: 'auto', persist: false},
        {name: 'short_name',  type: 'string'},
        {name: 'scale_points_percent',  type: 'int'},
        {name: 'deadline_handling',  type: 'int'},
        {name: 'delivery_types',  type: 'int'},
        {name: 'number_of_groups',  type: 'int', persist: false},
        {name: 'number_of_deliveries',  type: 'int', persist: false},
        {name: 'number_of_candidates',  type: 'int', persist: false},
        {name: 'number_of_groups_where_is_examiner',  type: 'int', persist: false},
        {name: 'has_valid_grading_setup', type: 'bool', persist: false},
        {name: 'gradingsystemplugin_title', type: 'string', persist: false},
        {name: 'max_points', type: 'int'},
        {name: 'passing_grade_min_points', type: 'int'},
        {name: 'points_to_grade_mapper', type: 'string'},
        {name: 'grading_system_plugin_id', type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/assignment/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    formatPublishOffsetFromNow: function() {
        return devilry_extjsextras.DatetimeHelpers.formatTimedeltaRelative(
            this.get('publishing_time_offset_from_now'), !this.get('is_published'));
    },

    formatPublishingTime: function() {
        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(this.get('publishing_time'));
    },
    formatFirstDeadline: function() {
        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(this.get('first_deadline'));
    },


    /** Get period info from breadcrumb.
     *
     * @return {Object} An object with ``id``, ``path`` and ``is_admin``. If ``is_admin`` is ``false``, ``id`` is ``null``.
     *
     * */
    getPeriodInfoFromBreadcrumb: function() {
        var breadcrumb = this.get('breadcrumb');
        var period_id;
        var periodpath;
        var is_admin;
        if(breadcrumb.length === 0) {
         throw "Breadcrumb is empty";
        } else if(breadcrumb.length === 1) {
            period_id = null;
            periodpath = breadcrumb[0].text.split('.').slice(0, 2).join('.');
            is_admin = false;
        } else {
            var periodpathArray = [];
            for(var index=0; index<breadcrumb.length-1; index++)  { // Exclude the last item (the assignment)
                var breadcrumbItem = breadcrumb[index];
                periodpathArray.push(breadcrumbItem.text);
            }
            period_id = breadcrumb[breadcrumb.length - 2].id;
            periodpath = periodpathArray.join('.');
            is_admin = true;
        }
        return {
            id: period_id,
            path: periodpath,
            is_admin: is_admin
        };
    }
});
