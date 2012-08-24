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
        {name: 'first_deadline',  type: 'date', "dateFormat": "Y-m-d H:i:s", persist: false},
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
        {name: 'delivery_types',  type: 'int'}
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
        return Ext.Date.format(this.get('publishing_time'), 'Y-m-d H:i');
    },


    /** Get period info from breadcrumb.
     *
     * @return {Object} An object with ``id``, ``short_name`` and ``path``. */
    getPeriodInfoFromBreadcrumb: function() {
        var breadcrumb = this.get('breadcrumb');
        var subjectBreadcrumb = breadcrumb[breadcrumb.length-2];
        var periodBreadcrumb = breadcrumb[breadcrumb.length-1];
        var periodpath = Ext.String.format('{0}.{1}', subjectBreadcrumb.short_name, periodBreadcrumb.short_name);
        return {
            id: periodBreadcrumb.id,
            short_name: periodBreadcrumb.short_name,
            path: periodpath
        };
    }
});
