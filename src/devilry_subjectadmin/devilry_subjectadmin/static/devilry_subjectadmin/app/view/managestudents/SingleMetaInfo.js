Ext.define('devilry_subjectadmin.view.managestudents.SingleMetaInfo', {
    extend: 'Ext.Component',
    alias: 'widget.singlegroupmetainfo',
    cls: 'devilry_subjectadmin_singlegroupmetainfo bootstrap',


    /**
     * @cfg {Ext.data.Model} [groupRecord]
     */

    tpl: [
        '<h3>', gettext('Grade') ,'</h3> ',
        '<tpl if="hasFeedback">',
            '<p>',
                '<tpl if="group.feedback.is_passing_grade">',
                    '<span class="success">',
                        gettext('Passed'),
                    '</span>',
                '<tpl else>',
                    '<span class="danger">',
                        gettext('Failed'),
                    '</span>',
                '</tpl>',
                ' <span class="grade">({group.feedback.grade})</span>',
                ' <small class="points">(',
                    gettext('Points'), ': {group.feedback.points}',
                ')</small>',
                '<br/>',
                '<small>',
                    '<strong>', gettext('Note'), ':</strong> ',
                    gettext('Students can not see their points, only the grade, and if it is failed or passed.'),
                '</small>',
            '</p>',
        '<tpl else>',
            '<p>',
                '<span class="label label-info">',
                    gettext('No feedback'),
                '</span>',
            '</p>',
        '</tpl>',

        '<h3>', gettext('Status'), '</h3>',
        '<p>',
            '<tpl if="group.is_open">',
                '<span class="label label-success">', gettext('Open'), '</span> ',
                gettext('The student(s) can add more deliveries.'),
            '<tpl else>',
                '<span class="label label-warning">', gettext('Closed'), '</span> ',
                gettext('The current grade is the final grade. The student(s) can <strong>not</strong> add more deliveries.'),
            '</tpl>',
            ' ', gettext('Examiners can open and close a group at any time to allow/prevent deliveries.'),
        '</p>',

        '<h3>', Ext.String.capitalize(gettext('Deliveries')) ,'</h3> ',
        '<p>{group.num_deliveries}</p>'
    ],


    initComponent: function() {
        this.data = {
            loading: false,
            hasFeedback: this.groupRecord.get('feedback') != null,
            group: this.groupRecord.data
        };
        this.callParent(arguments);
    }
});
