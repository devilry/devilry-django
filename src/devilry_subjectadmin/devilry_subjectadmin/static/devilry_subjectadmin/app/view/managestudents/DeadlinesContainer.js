Ext.define('devilry_subjectadmin.view.managestudents.DeadlinesContainer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.admingroupinfo_deadlinescontainer',
    cls: 'devilry_subjectadmin_admingroupinfo_deadlinescontainer devilry_discussionview_container',

    requires: [
        'devilry_subjectadmin.view.managestudents.DeadlinePanel',
        'devilry_extjsextras.AlertMessage'
    ],

    frame: false,
    border: false,
    bodyPadding: 0,
    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },

    populate: function(aggregatedGroupInfoRecord, active_feedback) {
        var deadlines = aggregatedGroupInfoRecord.get('deadlines');
        if(deadlines.length === 0) {
            this.add({
                xtype: 'alertmessage',
                type: 'error',
                title: gettext('No deadlines'),
                message: gettext('This group has no deadlines, so they can not add deliveries.')
            });
        } else {
            Ext.Array.each(deadlines, function(deadline) {
                this.add({
                    xtype: 'admingroupinfo_deadline',
                    deadline: deadline,
                    active_feedback: active_feedback
                });
            }, this);
        }

    }
});
