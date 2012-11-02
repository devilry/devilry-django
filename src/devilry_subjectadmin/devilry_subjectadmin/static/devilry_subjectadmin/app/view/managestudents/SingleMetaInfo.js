Ext.define('devilry_subjectadmin.view.managestudents.SingleMetaInfo', {
    extend: 'Ext.Container',
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

    initComponent: function() {
        Ext.apply(this, {
            layout: 'column',
            items: [{
                xtype: 'box',
                columnWidth: 0.6,
                margin: '0 5 0 0',
                cls: 'gradebox',
                tpl: [
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
                        '<div class="well well-small nofeedback muted">',
                            gettext('No feedback'),
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
                    group: this.groupRecord.data,
                    hasFeedback: this.groupRecord.get('feedback') !== null,
                    delivery_link_prefix: devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
                        this.assignment_id,
                        this.groupRecord.get('id'))
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
                cls: 'statusbox',
                columnWidth: 0.4,
                margin: '0 0 0 10',
                tpl: [
                    '<div class="alert alert-{[this.getStatusCls(values.group.is_open)]}">',
                        '<tpl if="group.is_open">',
                            '<strong class="status_open">', gettext('Open'), '</strong>: ',
                            '<small>',
                                gettext('The group can add more deliveries.'),
                            '</small>',
                        '<tpl else>',
                            '<strong class="status_closed">', gettext('Closed'), '</strong>: ',
                            '<small>',
                                gettext('The group can <strong>not</strong> add more deliveries.'),
                            '</small>',
                        '</tpl>',
                    '</div>', {
                        getStatusCls: function(is_open) {
                            return is_open? 'success': 'warning';
                        }
                    }
                ],
                data: {
                    group: this.groupRecord.data,
                    examinersNote: gettext('Examiners can open and close a group at any time to allow/prevent deliveries.')
                }
            }]
        });
        this.callParent(arguments);
    }

});
