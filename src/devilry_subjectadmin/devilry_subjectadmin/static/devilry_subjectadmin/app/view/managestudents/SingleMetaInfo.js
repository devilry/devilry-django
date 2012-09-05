Ext.define('devilry_subjectadmin.view.managestudents.SingleMetaInfo', {
    extend: 'Ext.Component',
    alias: 'widget.singlegroupmetainfo',
    cls: 'devilry_subjectadmin_singlegroupmetainfo bootstrap',

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],


    /**
     * @cfg {Ext.data.Model} [groupRecord]
     */

    /**
     * @cfg {String} [assignment_id]
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
                ' - <a class="active_feedback_link" href="{delivery_link_prefix}{group.feedback.delivery_id}">',
                    gettext('Details'),
                '</a>',

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
        '</p>'
    ],


    initComponent: function() {
        this.data = {
            hasFeedback: this.groupRecord.get('feedback') != null,
            group: this.groupRecord.data,
            delivery_link_prefix: devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
                this.assignment_id,
                this.groupRecord.get('id'))
        };
        this.callParent(arguments);
    }
});
