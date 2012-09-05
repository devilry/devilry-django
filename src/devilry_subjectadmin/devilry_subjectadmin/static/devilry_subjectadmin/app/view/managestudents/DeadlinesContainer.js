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
        if(deadlines.length == 0) {
            this.add({
                xtype: 'alertmessage',
                type: 'error',
                title: interpolate(gettext('No %(deadlines_term)s'), {
                    deadlines_term: gettext('deadlines')
                }, true),
                message: interpolate(gettext('This group has no %(deadlines_term)s, so they can not add %(deliveries_term)s.'), {
                    deadlines_term: gettext('deadlines'),
                    deliveries_term: gettext('deliveries')
                }, true)
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
