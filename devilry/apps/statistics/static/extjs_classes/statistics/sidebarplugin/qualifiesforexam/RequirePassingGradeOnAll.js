Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll', {
    extend: 'Ext.button.Button',
    text: 'Apply to all students',
    iconCls: 'icon-save-32',
    scale: 'large',
    //height: 30,
    //width: 200,

    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            listeners: {
                scope: this,
                click: this._onApply
            }
        });
        this.callParent(arguments);
    },

    _onApply: function() {
        this.loader.labelManager.setLabels({
            filter: this.filter,
            scope: this,
            label: this.labelname
        });
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
