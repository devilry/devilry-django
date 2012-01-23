Ext.define('subjectadmin.controller.Shortcuts', {
    extend: 'Ext.app.Controller',

    views: [
        'shortcut.List'
    ],

    stores: [
        'ActiveAssignments'
    ],

    refs: [{
        ref: 'shortcutList',
        selector: 'shortcutlist'
    }],


    init: function() {
        this.control({
            'viewport > shortcutlist': {
                render: function(list) {
                    this.getActiveAssignmentsStore().on('load', this._onActiveAssignmentsStoreLoad, this);
                    this.getActiveAssignmentsStore().load();
                }
            }
        });
    },


    _postProcessActiveAssignmentsData: function() {
        var store = this.getActiveAssignmentsStore();
        var subjects = store.collect('parentnode__parentnode__short_name');
        var results = []
        Ext.each(subjects, function(subject) {
            var recordsInSubject = store.queryBy(function(record) {
                return record.get('parentnode__parentnode__short_name') == subject;
            });
            var periods = recordsInSubject.collect('parentnode__short_name', 'data');
            var multiplePeriods = periods.length !== 1;
            var assignments = [];
            recordsInSubject.each(function(record) {
                var displayName = record.get('short_name');
                if(multiplePeriods) {
                    displayName = Ext.String.format('{0}.{1}', record.get('parentnode__short_name'), displayName);
                }
                assignments.push({
                    subject: record.get('parentnode__parentnode__short_name'),
                    period: record.get('parentnode__short_name'),
                    assignment: record.get('short_name'),
                    displayName: displayName
                });
            });
            results.push({
                subject: subject,
                assignments: assignments
            });
        });
        return results;
    },

    _onActiveAssignmentsStoreLoad: function() {
        this.getShortcutList().update({
            items: this._postProcessActiveAssignmentsData(),
        });
    }
});
