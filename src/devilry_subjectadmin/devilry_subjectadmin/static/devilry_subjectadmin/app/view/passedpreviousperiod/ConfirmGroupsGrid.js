Ext.define('devilry_subjectadmin.view.passedpreviousperiod.ConfirmGroupsGrid', {
    extend: 'devilry_subjectadmin.view.passedpreviousperiod.GridBase',
    alias: 'widget.confirmpassedpreviousgroupsgrid',
    cls: 'devilry_subjectadmin_editpassedpreviousgroupssgrid bootstrap',

//    disableSelection: true,

    addColumns:function () {
        this.columns.push({
            dataIndex: 'id',
            flex: 1,
            menuDisabled: true,
            renderer: this.renderoldOrIgnoredCol,
            sortable: false
        });
    }
});
