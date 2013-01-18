Ext.define('devilry_subjectadmin.view.examinerstats.SingleExaminerStatBox' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.singleexaminerstatobx',
    cls: 'devilry_subjectadmin_singleexaminerstatobx',

    requires: [
    ],

    /**
     * @cfg {devilry_subjectadmin.model.ExaminerStat} [examinerstat]
     */

    bodytpl: [
        '<h2>{examiner.user.displayname}</h2>',
        '<p>{examiner.id}</p>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: this.bodytpl,
                data: this.examinerstat.data
            }]
        });
        this.callParent(arguments);
    }
});