Ext.define('subjectadmin.view.chooseperiod.ActivePeriodsList', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.activeperiodslist',
    cls: 'activeperiodslist',
    store: 'ActivePeriods',
    hideHeaders: true,
    requires: [
        'Ext.XTemplate',
        'Ext.selection.CheckboxModel'
    ],

    // Would be nicer, however it does not work with back forward navigation
    // for some reason
    //selModel: Ext.create('Ext.selection.CheckboxModel', {
        //mode: 'SINGLE'
    //}),

    rowTpl: Ext.create('Ext.XTemplate',
        '<div class="important">{parentnode__short_name}.{short_name}</div>'
    ),

    multiSelect: false,

    columns: [{
        header: 'Name',  dataIndex: 'short_name',
        flex: 1,
        renderer: function(value, p, record) {
            return this.rowTpl.apply(record.data);
        }
    }]
});
