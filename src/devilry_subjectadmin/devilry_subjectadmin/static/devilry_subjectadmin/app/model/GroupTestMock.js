Ext.define('subjectadmin.model.GroupTestMock', {
    extend: 'subjectadmin.model.Group',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'groupproxy'
    }
});
