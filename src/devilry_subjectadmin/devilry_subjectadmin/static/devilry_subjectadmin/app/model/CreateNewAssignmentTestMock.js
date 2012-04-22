Ext.define('devilry_subjectadmin.model.CreateNewAssignmentTestMock', {
    extend: 'devilry_subjectadmin.model.CreateNewAssignment',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'createnewassginmentproxy',

        // We override this to force some error messages. This can be used to
        // test that errors are shown correctly, however not that errors are actually
        // received correctly.
        validator: function(operation) {
            var record = operation.getRecords()[0];
            var responseText = null;
            if(record.get('period_id') == 3) {
                responseText = {
                    errormessages: [
                        'This is a global error message',
                        'Another global message'
                    ],
                    fielderrors: {
                        short_name: ['Invalid short name'],
                        long_name: ['Invalid', 'Long name']
                    }
                };
                operation.setException({
                    status: 400,
                    statusText: "BAD REQUEST"
                });
            }

            // Trigger BAD REQUEST for publishing_time at the first of every month
            if(record.get('publishing_time').getDate() == 1) {
                responseText = {
                    errormessages: [
                        'This is a global error message',
                        'It is triggered since the day of month is "1" (for testing only).'
                    ]
                };
                operation.setException({
                    status: 400,
                    statusText: "BAD REQUEST"
                });
            }

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

            if(operation.hasException()) {
                var response = null;
                if(responseText) {
                    response = {responseText: Ext.JSON.encode(responseText)};
                }
                this.fireEvent('exception', this, response, operation);
            }
        }
    }
});
