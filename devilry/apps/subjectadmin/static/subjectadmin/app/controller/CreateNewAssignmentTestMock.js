Ext.define('subjectadmin.controller.CreateNewAssignmentTestMock', {
    extend: 'subjectadmin.controller.CreateNewAssignment',

    stores: [
        'ActiveAssignmentsTestMock'
    ],

    models: [
        'AssignmentTestMock'
    ],

    //_setInitialValues: function() {
        //this.getForm().getForm().setValues({
            //long_name: 'The first assignment',
            //short_name: 'firstassignment'
        //})
    //},

    getActiveAssignmentsStore: function() {
        return this.getActiveAssignmentsTestMockStore();
    },

    getAssignmentModel: function() {
        return this.getAssignmentTestMockModel();
    }
});
