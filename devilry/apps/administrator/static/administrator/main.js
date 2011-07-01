
Ext.require('devilry.administrator.NodeGrid');
Ext.onReady(function() {
    Ext.create('devilry.administrator.NodeGrid', {
        renderTo: 'nodegrid',
        title: 'Nodes',
        store: nodestore
    });

    Ext.create('devilry.administrator.NodeGrid', {
        renderTo: 'subjectgrid',
        title: 'Subjects',
        store: subjectstore
    });

    Ext.create('devilry.administrator.NodeGrid', {
        renderTo: 'periodgrid',
        store: periodstore,
        title: 'Periods'
    });
});
