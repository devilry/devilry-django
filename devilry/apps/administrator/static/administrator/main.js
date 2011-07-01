Ext.require('devilry.administrator.NodeGrid');
Ext.require('devilry.administrator.MultiNodeGridSearchField');
Ext.require('devilry.administrator.MultiNodeGrid');
Ext.onReady(function() {
    var searchresults = Ext.create('devilry.administrator.MultiNodeGrid', {
        renderTo: 'searchresults',
        items: [{
            xtype: 'administrator-nodegrid',
            title: 'Nodes',
            store: nodestore
        }, {
            xtype: 'administrator-nodegrid',
            title: 'Subjects',
            store: subjectstore
        }, {
            xtype: 'administrator-nodegrid',
            title: 'Periods',
            store: periodstore
        }]
    });

    var searchfield = Ext.create('devilry.administrator.MultiNodeGridSearchField', {
        resultContainer: searchresults
    });
    searchfield.focus();

});
