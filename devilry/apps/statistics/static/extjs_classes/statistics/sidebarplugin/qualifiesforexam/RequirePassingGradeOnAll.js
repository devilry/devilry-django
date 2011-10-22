Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: this.defaultButtonPanel
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var passes = 0;
        Ext.each(this.loader.assignment_ids, function(assignment_id, index) {
            var group = student.get('groupsByAssignmentId')[assignment_id];
            if(group && group.is_passing_grade) {
                passes ++;
            }
        }, this);
        //console.log(student.get('groupsByAssignmentId'));
        return passes == Ext.Object.getSize(student.get('groupsByAssignmentId'));
        //return true;
    }
});
