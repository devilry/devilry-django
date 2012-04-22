Ext.define('devilry_subjectadmin.store.ActiveAssignmentsTestMock', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.ActiveAssignmentTestMock',

    loadActiveAssignments: function(config) {
        this.load(config);
    }
});
