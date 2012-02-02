Ext.define('subjectadmin.controller.AssignmentTestMock', {
    extend: 'subjectadmin.controller.Assignment',

    stores: [
        'SingleAssignmentTestMock'
    ],

    init: function() {
        var initialData = [{
            id: 0,
            parentnode__parentnode__short_name:'duck1100',
            parentnode__short_name:'2012h',
            short_name:'week1'
        }, {
            id: 1,
            parentnode__parentnode__short_name:'duck1100',
            parentnode__short_name:'2012h',
            short_name:'week2'
        }, {
            id: 2,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode__short_name:'2012h',
            short_name:'assignment1'
        }, {
            id: 3,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode__short_name:'2012h',
            short_name:'assignment2'
        }, {
            id: 4,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode__short_name:'2012h-extra',
            short_name:'extra'
        }];

        this.getSingleAssignmentTestMockStore().proxy.setData(initialData);
        this.callParent();
    },

    getSingleAssignmentStore: function() {
        return this.getSingleAssignmentTestMockStore();
    }
});
