Ext.define('devilry_subjectadmin.view.createnewassignment.SelectSingleAssignment', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.selectsingleassignment',
    requires: [
    ],

    store: 'Assignments',
    queryMode: 'local',
    forceSelection: true,
    editable: false,
    displayField: 'long_name',
    valueField: 'id',
    hideLabel: true,
    listConfig: {
        cls: 'selectsingleassignment_boundlist'
    }
    //labelWidth: 200,
    //fieldLabel: gettext('Select an assignment')
});
