Ext.define('subjectadmin.model.AssignmentTestMock', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedAssignment',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'simplifiedassignmentproxy',
        //show: true,

        // We override this to force some error messages. This can be used to
        // test that errors are shown correctly, however not that errors are actually
        // received correctly.
        validator: function(operation) {
            var record = operation.getRecords()[0];

            // Trigger BAD REQUEST for publishing_time at the first of every month
            if(record.get('publishing_time').getDate() == 1) {
                operation.responseData = {
                    items: {
                        errormessages: [
                            'This is a global error message',
                            'It is triggered since the day of month is "1" (for testing only).'
                        ]
                    }
                };
                operation.setException({
                    status: 400,
                    statusText: "BAD REQUEST"
                });
            }
        }
    }
});
