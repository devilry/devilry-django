Ext.define('subjectadmin.store.ActivePeriods', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.Period',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/administrator/restfulsimplifiedperiod/',
        result_fieldgroups: ["period", "subject"],
        orderby: ['-start_time']
    }),

    loadActivePeriods: function(config) {
        this.proxy.extraParams.limit = 100000;

        var now = Ext.Date.format(new Date(Ext.Date.now()), 'Y-m-d H:i:s');
        this.proxy.setDevilryFilters([{
            field: 'start_time',
            comp: '<',
            value: now
        }, {
            field: 'end_time',
            comp: '>',
            value: now
        }]);
        this.load(config);
    }
});
