/**
 * The grid that shows students on a single group.
 */
Ext.define('subjectadmin.view.managestudents.StudentsInGroupGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.studentsingroupgrid',
    cls: 'studentsingroupgrid',
    hideHeaders: true,
    requires: [
        'Ext.XTemplate'
    ],

    rowTpl: ['{student__devilryuserprofile__full_name} <small>({student__username})</small>'],

    title: dtranslate('subjectadmin.managestudents.students.title'),
    columns: [{
        header: 'Name',
        flex: 1,
        dataIndex: 'student__devilryuserprofile__full_name',
        renderer: function(unused1, unused2, studentRecord) {
            return Ext.create('Ext.XTemplate', this.rowTpl).apply(studentRecord.data);
        }
    }]
});
