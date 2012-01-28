Ext.define('subjectadmin.controller.CreateNewAssignmentTestMock', {
    extend: 'subjectadmin.controller.CreateNewAssignment',

    stores: [
        'ActiveAssignmentsTestMock'
    ],

    _setInitialValues: function() {
        this.getForm().getForm().setValues({
            long_name: 'The first assignment',
            short_name: 'firstassignment'
        })
    },
});
