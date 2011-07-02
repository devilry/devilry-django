Ext.require('devilry.administrator.SearchResults');
Ext.require('devilry.administrator.MultiSearchField');
Ext.require('devilry.administrator.MultiSearchResults');
Ext.onReady(function() {
    var searchwidget = Ext.create('devilry.administrator.SearchWidget', {
        renderTo: 'searchresults',
        searchResultItems: [{
            xtype: 'administratorsearchresults',
            title: 'Nodes',
            store: nodestore
        }, {
            xtype: 'administratorsearchresults',
            title: 'Subjects',
            store: subjectstore
        }, {
            xtype: 'administratorsearchresults',
            title: 'Periods',
            store: periodstore
        }]
    });

    searchwidget.focusOnSearchfield();
});
