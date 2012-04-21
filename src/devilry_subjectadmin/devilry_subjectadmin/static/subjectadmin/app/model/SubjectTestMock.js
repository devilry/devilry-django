/** Test mockup model for Subject. */
Ext.define('subjectadmin.model.SubjectTestMock', {
    extend: 'devilry.apps.administrator.simplified.SimplifiedSubject',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'simplifiedsubjectproxy',

        validator: function(operation) {
        }
    }
});
