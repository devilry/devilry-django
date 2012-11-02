Ext.define('devilry_subjectadmin.view.managestudents.SingleMetaInfo', {
    extend: 'Ext.Container',
    alias: 'widget.singlegroupmetainfo',
    cls: 'devilry_subjectadmin_singlegroupmetainfo bootstrap',

    requires: [
        'devilry_subjectadmin.utils.UrlLookup'
    ],


    initComponent: function() {
        Ext.apply(this, {
            layout: 'column',
            items: [{
                xtype: 'box',
                columnWidth: 0.6,
                margin: '0 5 0 0',
                cls: 'gradebox',
                itemId: 'gradebox',
                tpl: [
                    '<tpl if="!loading">',
                        '<tpl if="hasFeedback">',
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
                            '<div class="well well-small nofeedback muted"><p style="margin: 0; padding: 0;">',
                                gettext('No feedback'),
                            '</p></div>',
                        '</tpl>',
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
                listeners: {
                    element: 'el',
                    delegate: 'a.active_feedback_link',
                    scope: this,
                    click: function(e) {
                        e.preventDefault();
                        this.fireEvent('active_feedback_link_clicked');
                    }
                }
            }, {
                xtype: 'box',
                columnWidth: 0.4,
                margin: '0 0 0 10',
                cls: 'statusbox',
                itemId: 'statusbox',
                tpl: [
                    '<tpl if="!loading">',
                        '<tpl if="group.is_open">',
                            '<div class="alert alert-info">',
                                '<strong class="status_open">', gettext('Open'), '</strong>: ',
                                '<small>',
                                    gettext('The group can add more deliveries.'),
                                '</small>',
                            '</div>',
                        '<tpl else>',
                            '<div class="well well-small muted"><p style="margin:0; padding:0;">',
                                '<strong class="status_closed">', gettext('Closed'), '</strong>: ',
                                '<small>',
                                    gettext('The group can <strong>not</strong> add more deliveries.'),
                                '</small>',
                            '</p></div>',
                        '</tpl>',
                    '</tpl>'
                ],
                data: {
                    loading: true
                }
            }]
        });
        this.callParent(arguments);
    },


    /**
     * @param {devilry_subjectadmin.model.Group} groupRecord (required)
     */
    setGroupRecord: function(groupRecord) {
        this.down('#gradebox').update({
            loading: false,
            group: groupRecord.data,
            hasFeedback: groupRecord.get('feedback') !== null,
            delivery_link_prefix: devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
                groupRecord.get('id'))
        });
        this.down('#statusbox').update({
            group: groupRecord.data,
            examinersHint: gettext('Examiners can open and close a group at any time to allow/prevent deliveries.'),
            loading: false
        });
    }
});
