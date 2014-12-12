Ext.define('devilry_subjectadmin.view.relatedstudents.Grid', {
    extend: 'devilry_subjectadmin.view.relatedexaminers.Grid',
    alias: 'widget.relatedstudentsgrid',
    cls: 'devilry_subjectadmin_relatedusergrid devilry_subjectadmin_relatedstudentsgrid bootstrap',
    requires: [
        'Ext.grid.plugin.CellEditing'
    ],

    store: 'RelatedStudents',

    initExtra: function() {
        var editingPlugin = Ext.create('Ext.grid.plugin.CellEditing', {
            clicksToEdit: 2
        });
        this.columns.push({
            dataIndex: 'candidate_id',
            itemId: 'candidateColumn',
            flex: 2,
            header: gettext('Candidate ID'),
            editor: {
                xtype: 'textfield'
            }
        });
        this.plugins = [editingPlugin];
        this.callParent(arguments);
    }
});
