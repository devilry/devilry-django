Ext.require('devilry.administrator.SearchWidget');
Ext.onReady(function() {
    var searchwidget = Ext.create('devilry.administrator.SearchWidget', {
        renderTo: 'searchwidget',
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
            store: periodstore,
            formatRow: function(record) {
                return this.getFormattedRow(
                    record.get('long_name'),
                    Ext.String.format('{0}.{1}',
                        record.get('parentnode__short_name'),
                        record.get('short_name')));
            }
        }]
    });

    searchwidget.focusOnSearchfield();
});
