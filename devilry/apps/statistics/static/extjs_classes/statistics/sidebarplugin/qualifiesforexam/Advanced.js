Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                cls: 'readable-section',
                html: '<strong>Coming soon.</strong> If the other methods do not cover your needs, you can track our progress towards an advanced filter on <a href="https://github.com/devilry/devilry-django/issues/236">our issue tracker</a>.'
            }]
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
        return false;
    }
});
