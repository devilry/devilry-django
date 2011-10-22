Ext.define('devilry.statistics.AggregatedPeriodDataForStudentBase', {
    extend: 'Ext.data.Model',

    constructor: function(config) {
        this.callParent([config]);
    },

    setLabel: function(label, value) {
        var labels = this.get('labels');
        labels[label] = value;
        this.set('labels', labels);
        this.set('labelKeys', Ext.Object.getKeys(labels));
    },

    delLabel: function(label) {
        var labels = this.get('labels');
        delete labels[label];
        this.set('labels', labels);
        this.set('labelKeys', Ext.Object.getKeys(labels));
    },

    passesAssignments: function(assignment_ids) {
        var passes = 0;
        Ext.Object.each(this.get('groupsByAssignmentId'), function(assignment_id, group) {
            if(Ext.Array.contains(assignment_ids, parseInt(assignment_id))) {
                if(group.is_passing_grade) {
                    passes ++;
                }
            };
        }, this);
        return passes === assignment_ids.length;
    }
});
