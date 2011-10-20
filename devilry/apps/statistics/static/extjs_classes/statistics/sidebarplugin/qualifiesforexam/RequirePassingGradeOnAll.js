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
        this.loader.setLabels({
            callback: function(student) {
                var passes = 0;
                Ext.Object.each(student.groupsByAssignmentId, function(key, group) {
                    if(group.is_passing_grade) {
                        passes ++;
                    }
                }, this);
                return {
                    labelname: this.labelname,
                    apply: passes == Ext.Object.getSize(student.groupsByAssignmentId)
                };
            },
            scope: this,
            mode: 'update'
        });
    }
});
