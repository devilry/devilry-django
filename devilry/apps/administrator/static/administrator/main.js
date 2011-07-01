Ext.require('devilry.administrator.NodeGrid');
Ext.require('devilry.administrator.MultiNodeGridSearchField');
Ext.onReady(function() {


    var searchfield = Ext.create('devilry.administrator.MultiNodeGridSearchField', {
        resultgrids: [
            Ext.create('devilry.administrator.NodeGrid', {
                renderTo: 'nodegrid',
                title: 'Nodes',
                store: nodestore
            }),

            Ext.create('devilry.administrator.NodeGrid', {
                renderTo: 'subjectgrid',
                title: 'Subjects',
                store: subjectstore
            }),

            Ext.create('devilry.administrator.NodeGrid', {
                renderTo: 'periodgrid',
                store: periodstore,
                title: 'Periods'
            })
        ]
    });

    searchfield.focus();
});
