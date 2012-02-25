Ext.define('subjectadmin.controller.CreateNewAssignmentTestMock', {
    extend: 'subjectadmin.controller.CreateNewAssignment',

    models: [
        'CreateNewAssignmentTestMock'
    ],

    //_setInitialValues: function() {
        //this.getForm().getForm().setValues({
            //long_name: 'The first assignment',
            //short_name: 'firstassignment'
        //})
    //},

    //getActiveAssignmentsStore: function() {
        //return this.getActiveAssignmentsTestMockStore();
    //},

    getCreateNewAssignmentModel: function() {
        return this.getCreateNewAssignmentTestMockModel();
    }
});
