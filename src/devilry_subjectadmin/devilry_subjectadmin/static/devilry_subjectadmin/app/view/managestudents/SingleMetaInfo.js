Ext.define('devilry_subjectadmin.view.managestudents.SingleMetaInfo', {
    extend: 'Ext.Component',
    alias: 'widget.singlegroupmetainfo',
    cls: 'devilry_subjectadmin_singlegroupmetainfo bootstrap',

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    tpl: [
        '<tpl if="!loading">',
            '<div class="status-{status}">',
                '<tpl if="status === \'corrected\'">',
                    '<div class="alert alert-{[this.getFeedbackCls(values.group.feedback)]}">',
                        '<strong>', gettext('Grade') ,':</strong> ',
               
                        '<tpl if="group.feedback.is_passing_grade">',
                            '<span class="passing_grade">',
                                gettext('Passed'),
                            '</span>',
                        '<tpl else>',
                            '<span class="failing_grade">',
                                gettext('Failed'),
                            '</span>',
                        '</tpl>',
                        ' <span class="grade">({group.feedback.grade})</span>',
                        ' <small class="points">(',
                            gettext('Points'), ': {group.feedback.points}',
                        ')</small>',
                        ' - <a class="active_feedback_link" href="{delivery_link_prefix}{group.feedback.delivery_id}"><small>',
                            gettext('Details'),
                        '</small></a>',
               
                        '<br/><small>',
                            '<strong>', gettext('Note'), ':</strong> ',
                            gettext('Students can not see their points, only the grade, and if it is failed or passed.'),
                        '</small>',
                    '</div>',
                '<tpl else>',
                    '<div class="well well-small muted"><p style="margin: 0; padding: 0;">',
                        '<tpl if="status === \'waiting-for-deliveries\'">',
                            '<em><small class="muted">', gettext('Waiting for deliveries'), '</small></em>',
                        '<tpl elseif="status === \'waiting-for-feedback\'">',
                            '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                        '<tpl else>',
                            '<span class="label label-important">{status}</span>',
                        '</tpl>',
                    '</p></div>',
                '</tpl>',
            '</div>',
        '</tpl>', {
            getFeedbackCls: function(feedback) {
                if(feedback.is_passing_grade) {
                    return 'success';
                } else {
                    return 'warning';
                }
            }
        }
    ],

    data: {
        loading: true
    },


    initComponent: function() {
        this.callParent(arguments);
        this.on({
            element: 'el',
            delegate: 'a.active_feedback_link',
            scope: this,
            click: function(e) {
                e.preventDefault();
                this.fireEvent('active_feedback_link_clicked');
            }
        });
    },


    /**
     * @param {devilry_subjectadmin.model.Group} groupRecord (required)
     */
    setGroupRecord: function(groupRecord) {
        this.update({
            loading: false,
            group: groupRecord.data,
            'status': groupRecord.get('status'),
            delivery_link_prefix: devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
                groupRecord.get('id'))
        });
    }
});
