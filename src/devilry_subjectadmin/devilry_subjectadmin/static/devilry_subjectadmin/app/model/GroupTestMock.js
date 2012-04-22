Ext.define('devilry_subjectadmin.model.GroupTestMock', {
    extend: 'devilry_subjectadmin.model.Group',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'groupproxy'
    }
});
