Ext.define('subjectadmin.controller.subject.OverviewTestMock', {
    extend: 'subjectadmin.controller.subject.Overview',

    stores: [
        'SubjectsTestMock'
    ],

    init: function() {
        var initialData = [{
            id: 0,
            short_name:'duck1100',
            long_name:'DUCK 1100 - Introduction to Python programming'
        }, {
            id: 1,
            short_name:'duck-mek2030',
            long_name: 'DUCK-MEK 2030 - Something Mechanical'
        }];

        // Add data to the proxy. This will be available in the store after a
        // load(), thus simulating loading from a server.
        var store = this.getSubjectsTestMockStore();
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.SubjectTestMock', data);
            record.phantom = true; // Force create
            record.save({
                failure: function(r, op) {
                    //console.log('fail', op);
                }
            });
        }, this);

        this.callParent();
    },

    getSubjectsStore: function() {
        return this.getSubjectsTestMockStore();
    }
});
