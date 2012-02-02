Ext.define('subjectadmin.store.SingleAssignmentTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.AssignmentTestMock',
    requires: [
        'Ext.data.Operation'
    ],

    loadAssignment: function(subject_shortname, period_shortname, assignment_shortname, callbackFn, callbackScope) {
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
    }
});
