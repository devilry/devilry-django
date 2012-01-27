Ext.define('subjectadmin.view.ActivePeriodsList', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.activeperiodslist',
    cls: 'activeperiodslist',
    store: 'ActivePeriods',
    hideHeaders: true,
    requires: [
        'Ext.XTemplate',
        'Ext.selection.CheckboxModel'
    ],
    selModel: Ext.create('Ext.selection.CheckboxModel'),

    rowTpl: Ext.create('Ext.XTemplate',
        '<div class="important">{parentnode__short_name}.{short_name}</div>'
    ),

    columns: [{
        header: 'Name',  dataIndex: 'short_name',
        flex: 1,
        renderer: function(value, p, record) {
            return this.rowTpl.apply(record.data);
        }
    }]
});
