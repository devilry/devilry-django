Ext.define('subjectadmin.controller.assignment.OverviewTestMock', {
    extend: 'subjectadmin.controller.assignment.Overview',

    stores: [
        'AssignmentsTestMock'
    ],

    //init: function() {
        //var dateformat = 'Y-m-d\\TH:i:s';
        //var now = new Date();
        //var yesterdayDate = Ext.Date.add(now, Ext.Date.DAY, -1);
        //if(yesterdayDate.getDate() == 1) { // Needed to avoid hitting the fake error raising in model.AssignmentTestMock
            //yesterdayDate = Ext.Date.add(yesterdayDate, Ext.Date.DAY, -1);
        //}
        //var yesterday = Ext.Date.format(yesterdayDate, dateformat);
        //var nextmonth = Ext.Date.format(Ext.Date.add(yesterdayDate, Ext.Date.MONTH, 1), dateformat);
        //var initialData = [{
            //id: 0,
            //parentnode__parentnode__short_name:'duck1100',
            //parentnode__short_name:'2012h',
            //parentnode:2,
            //long_name:'The one and only week one',
            //publishing_time: yesterday,
            //short_name:'week1'
        //}, {
            //id: 1,
            //parentnode__parentnode__short_name:'duck1100',
            //parentnode__short_name:'2012h',
            //parentnode:2,
            //long_name:'The one and only week two',
            //publishing_time: nextmonth,
            //short_name:'week2'
        //}, {
            //id: 4,
            //parentnode__parentnode__short_name:'duck-mek2030',
            //parentnode:1,
            //parentnode__short_name:'2012h-extra',
            //publishing_time: nextmonth,
            //long_name: 'Extra superhard assignment',
            //short_name:'extra'
        //}];

        //// Add data to the proxy. This will be available in the store after a
        //// load(), thus simulating loading from a server.
        //var store = this.getAssignmentsTestMockStore();
        //Ext.Array.each(initialData, function(data) {
            //var record = Ext.create('subjectadmin.model.AssignmentTestMock', data);
            //record.phantom = true; // Force create
            //record.save({
                //failure: function(r, op) {
                    ////console.log('fail', op);
                //}
            //});
        //}, this);

        ////this.getAssignmentsTestMockStore().proxy.setData(initialData);
        //this.callParent();
    //},

    getAssignmentsStore: function() {
        return this.getAssignmentsTestMockStore();
    }
});
