Ext.define('subjectadmin.store.SubjectsTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.SubjectTestMock',

    loadSubject: function(subject_shortname, callbackFn, callbackScope) {
        this._loadData();
        this.load({
            scope: this,
            callback: function() {
                // Mock the results of setDevilryFilters
                var index = this.findBy(function(record) {
                    return record.get('short_name') == subject_shortname;
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

    _loadData: function() {
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
        Ext.Array.each(initialData, function(data) {
            var record = Ext.create('subjectadmin.model.SubjectTestMock', data);
            record.phantom = true; // Force create
            record.save({
                failure: function(r, op) {
                    //console.log('fail', op);
                }
            });
        }, this);
    },

    loadAll: function(config) {
        console.log(config);

        // Simulate servererror if ``servererror`` in querystring
        var query = Ext.Object.fromQueryString(window.location.search);
        if(query.servererror) {
            var operation = Ext.create('Ext.data.Operation');
            operation.setException({
                status: 500,
                statusText: "Server error"
            });
            Ext.callback(config.callback, config.scope, [undefined, operation]);
            return;
        }

        this._loadData();

        this.load(config);
    }
});
