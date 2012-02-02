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
            long_name:'The one and only week one',
            short_name:'week1'
        }, {
            id: 1,
            parentnode__parentnode__short_name:'duck1100',
            parentnode__short_name:'2012h',
            long_name:'The one and only week two',
            short_name:'week2'
        }, {
            id: 2,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode__short_name:'2012h',
            long_name:'First assignment',
            short_name:'assignment1'
        }, {
            id: 3,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode__short_name:'2012h',
            long_name:'Second assignment',
            short_name:'assignment2'
        }, {
            id: 4,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode__short_name:'2012h-extra',
            long_name: 'Extra superhard assignment',
            short_name:'extra'
        }];

        // Add data to the proxy. This will be available in the store after a
        // load(), thus simulating loading from a server.
        var store = this.getSingleAssignmentTestMockStore();
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.AssignmentTestMock', data);
            record.phantom = true; // Force create
            record.save();
        }, this);

        //this.getSingleAssignmentTestMockStore().proxy.setData(initialData);
        this.callParent();
    },

    getSingleAssignmentStore: function() {
        return this.getSingleAssignmentTestMockStore();
    }
});
