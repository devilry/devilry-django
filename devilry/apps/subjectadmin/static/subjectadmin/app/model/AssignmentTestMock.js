Ext.define('subjectadmin.model.AssignmentTestMock', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'simplifiedassignmentproxy',
        validator: function(action, operation) {
            var record = operation.getRecords()[0];
            //if(record.get('parentnode') == '2') {
            //}

            if(record.get('short_name') == 'servererror') {
                operation.setException({
                    status: 500,
                    statusText: "Server error"
                });
            } else if(record.get('short_name') == 'noconnection') {
                operation.setException({
                    status: 0
                });
            }
        }
    }
});
