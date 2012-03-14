Ext.define('subjectadmin.store.SubjectsTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.SubjectTestMock',

    loadSubject: function(subject_shortname, callbackFn, callbackScope) {
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
    }
});
