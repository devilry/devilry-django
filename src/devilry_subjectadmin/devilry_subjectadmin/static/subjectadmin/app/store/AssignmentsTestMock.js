Ext.define('subjectadmin.store.AssignmentsTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.AssignmentTestMock',
    requires: [
        'Ext.data.Operation'
    ],

    loadAssignment: function(subject_shortname, period_shortname, assignment_shortname, callbackFn, callbackScope) {
        this._addDataToStore();
        this.load({
            scope: this,
            callback: function() {
                // Mock the results of setDevilryFilters
                var index = this.findBy(function(record) {
                    //console.log('findBy',
                        //record.get('parentnode__parentnode__short_name'),
                        //record.get('parentnode__short_name'),
                        //record.get('short_name')
                    //);
                    return (
                        record.get('parentnode__parentnode__short_name') == subject_shortname
                        && record.get('parentnode__short_name') == period_shortname
                        && record.get('short_name') == assignment_shortname
                    );
                });

                var operation = Ext.create('Ext.data.Operation', {
                    action: 'read'
                });
                operation.setStarted();
                var success = index != -1;
                var records = [];
                if(success) {
                    operation.setSuccessful();
                    records = [this.getAt(index)];
                } else {
                    operation.setException({
                        status: 400,
                        statusText: 'Error'
                    });
                }

                Ext.callback(callbackFn, callbackScope, [records, operation]);
            }
        })
    },

    _addDataToStore: function() {
        var dateformat = 'Y-m-d\\TH:i:s';
        var now = new Date();
        var yesterdayDate = Ext.Date.add(now, Ext.Date.DAY, -1);
        if(yesterdayDate.getDate() == 1) { // Needed to avoid hitting the fake error raising in model.AssignmentTestMock
            yesterdayDate = Ext.Date.add(yesterdayDate, Ext.Date.DAY, -1);
        }
        var yesterday = Ext.Date.format(yesterdayDate, dateformat);
        var nextmonth = Ext.Date.format(Ext.Date.add(yesterdayDate, Ext.Date.MONTH, 1), dateformat);
        var initialData = [{
            id: 0,
            parentnode__parentnode__short_name:'duck1100',
            parentnode__short_name:'2012h',
            parentnode:2,
            long_name:'The one and only week one',
            publishing_time: yesterday,
            short_name:'week1'
        }, {
            id: 1,
            parentnode__parentnode__short_name:'duck1100',
            parentnode__short_name:'2012h',
            parentnode:2,
            long_name:'The one and only week two',
            publishing_time: nextmonth,
            short_name:'week2'
        }, {
            id: 4,
            parentnode__parentnode__short_name:'duck-mek2030',
            parentnode:1,
            parentnode__short_name:'2012h-extra',
            publishing_time: nextmonth,
            long_name: 'Extra superhard assignment',
            short_name:'extra'
        }];

        // Add data to the proxy. This will be available in the store after a
        // load(), thus simulating loading from a server.
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.AssignmentTestMock', data);
            record.phantom = true; // Force create
            record.save({
                //success: function(r) {
                    //console.log(r);
                //},
                //failure: function(r, op) {
                    //console.log('fail', op);
                //}
            });
        }, this);
    },

    loadAssignmentsInPeriod: function(subject_shortname, period_shortname, callbackFn, callbackScope) {
        // Simulate servererror if ``servererror`` in querystring
        var query = Ext.Object.fromQueryString(window.location.search);
        if(query.servererror) {
            var operation = Ext.create('Ext.data.Operation');
            operation.setException({
                status: 500,
                statusText: "Server error"
            });
            Ext.callback(callbackFn, callbackScope, [undefined, operation]);
            return;
        }

        this._addDataToStore();

        this.load({
            scope: this,
            callback: function(records, operation) {
                this.filterBy(function(record) {
                    return (record.get('parentnode__parentnode__short_name') == subject_shortname &&
                            record.get('parentnode__short_name') == period_shortname);
                });
                Ext.callback(callbackFn, callbackScope, [this.data.items, operation]);
            }
        });
    }
});
