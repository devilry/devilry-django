Ext.require('devilry.administrator.SearchResults');
Ext.require('devilry.administrator.MultiSearchField');
Ext.require('devilry.administrator.MultiSearchResults');
Ext.onReady(function() {
    var searchresults = Ext.create('devilry.administrator.MultiSearchResults', {
        renderTo: 'searchresults',
        items: [{
            xtype: 'administrator-searchresults',
            title: 'Nodes',
            store: nodestore
        }, {
            xtype: 'administrator-searchresults',
            title: 'Subjects',
            store: subjectstore
        }, {
            xtype: 'administrator-searchresults',
            title: 'Periods',
            store: periodstore
        }]
    });

    var searchfield = Ext.create('devilry.administrator.MultiSearchField', {
        resultContainer: searchresults
    });
    searchfield.focus();

});
