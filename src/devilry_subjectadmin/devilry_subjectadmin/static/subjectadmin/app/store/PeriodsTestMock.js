Ext.define('subjectadmin.store.PeriodsTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.PeriodTestMock',

    loadPeriod: function(subject_shortname, period_shortname, callbackFn, callbackScope) {
        this._addDataToStore();
        this.load({
            scope: this,
            callback: function() {
                // Mock the results of setDevilryFilters
                var index = this.findBy(function(record) {
                    return (record.get('parentnode__short_name') == subject_shortname &&
                            record.get('short_name') == period_shortname);
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
        var initialData = [{
            id: 1,
            parentnode__short_name: 'duck1100',
            short_name: '2012h',
            long_name: 'Spring 2012'
        }, {
            id: 2,
            parentnode__short_name:'duck-mek2030',
            short_name: '2012h',
            long_name: 'Spring 2012'
        }, {
            id: 3,
            parentnode__short_name:'duck-mek2030',
            short_name: '2012h-extra',
            long_name: 'Spring 2012 extra assignments'
        }];

        // Add data to the proxy. This will be available in the store after a
        // load(), thus simulating loading from a server.
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.PeriodTestMock', data);
            record.phantom = true; // Force create
            record.save({
                failure: function(r, op) {
                    //console.log('fail', op);
                }
            });
        }, this);
    },

    loadPeriodsInSubject: function(subject_shortname, callbackFn, callbackScope) {
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
                    return record.get('parentnode__short_name') == subject_shortname;
                });
                Ext.callback(callbackFn, callbackScope, [this.data.items, operation]);
            }
        });
    }
});
