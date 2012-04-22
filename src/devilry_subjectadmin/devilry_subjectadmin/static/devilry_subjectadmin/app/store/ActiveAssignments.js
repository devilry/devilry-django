Ext.define('devilry_subjectadmin.store.ActiveAssignments', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.ActiveAssignment',
    requires: [
        'Ext.Date'
    ],

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedassignment/',
        result_fieldgroups: ["period", "subject"],
        orderby: ['-publishing_time']
    }),

    loadActiveAssignments: function(config) {
        this.proxy.extraParams.limit = 100000;

        var now = Ext.Date.format(new Date(Ext.Date.now()), 'Y-m-d H:i:s');
        this.proxy.setDevilryFilters([{
            field: 'parentnode__start_time',
            comp: '<',
            value: now
        }, {
            field: 'parentnode__end_time',
            comp: '>',
            value: now
        }]);
        this.load(config);
    }
});
