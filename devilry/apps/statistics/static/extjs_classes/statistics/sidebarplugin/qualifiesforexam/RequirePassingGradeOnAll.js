Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: this.saveButton
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var passes = 0;
        Ext.each(this.loader.assignment_ids, function(assignment_id, index) {
            var group = student.groupsByAssignmentId[assignment_id];
            if(group && group.is_passing_grade) {
                passes ++;
            }
        }, this);
        return passes == Ext.Object.getSize(student.groupsByAssignmentId);
    }
});
