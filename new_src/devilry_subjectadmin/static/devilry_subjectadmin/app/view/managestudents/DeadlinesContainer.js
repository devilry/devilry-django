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

    populate: function(aggregatedGroupInfoRecord, active_feedback, delivery_types) {
        var deadlines = aggregatedGroupInfoRecord.get('deadlines');
        if(deadlines.length === 0) {
            this.add({
                xtype: 'alertmessage',
                type: 'error',
                title: gettext('No deadlines'),
                message: gettext('This group has no deadlines. This is probably caused by a third-party plugin or integration script behaving incorrectly, or it may be a bug in Devilry.')

            });
        } else {
            if(delivery_types === 0) {
                Ext.Array.each(deadlines, function(deadline) {
                    this.add({
                        xtype: 'admingroupinfo_deadline',
                        deadline: deadline,
                        active_feedback: active_feedback
                    });
                }, this);
            } else {
                if(deadlines.length === 1) {
                    this.add({
                        xtype: 'admingroupinfo_deadline',
                        deadline: deadlines[0],
                        non_electronic: true,
                        active_feedback: active_feedback
                    });
                } else {
                    this.add({
                        xtype: 'alertmessage',
                        type: 'error',
                        title: gettext('More than one deadline on non-electronic assignment'),
                        message: gettext('Devilry does not support deadlines for non-electronic assignments. To avoid special handling of non-electronic assignments, we create EXACTLY ONE dummy-deadline. This assignment is non-electronic, but it has more than one deadline. The most likely cause is a third-party integration with Devilry that handles non-electronic assignments incorrectly, or a bug in Devilry.')
                    });
                }
            }
        }
    }
});
