Ext.define('subjectadmin.store.ActiveAssignmentsTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.ActiveAssignmentTestMock',

    loadActiveAssignments: function(config) {
        this.load(config);
    }
});
