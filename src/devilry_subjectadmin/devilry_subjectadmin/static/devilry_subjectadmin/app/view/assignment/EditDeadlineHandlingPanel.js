/**
 * A panel for editing the deadline_handling attribute of an Assignment.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditDeadlineHandlingPanel', {
    extend: 'devilry_extjsextras.OkCancelPanel',
    alias: 'widget.editdeadline_handlingpanel',
    cls: 'devilry_subjectadmin_editdeadline_handlingpanel bootstrap',

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            oktext: gettext('Save'),
            items: {
                xtype: 'form',
                bodyPadding: 10,
                autoScroll: true,
                border: 0,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'box',
                    tpl: [
                        '<p>',
                            gettext('Enable hard deadlines if you want to make it impossible for {students_term} to add deliveries after their active deadline.'),
                        '</p>',
                        '<p><small class="muted">',
                            gettext('NOTE: Devilry is designed from the bottom up to gracefully handle SOFT deadlines. Students have to perform an extra confirm-step when adding deliveries after their active deadline, and assignments where the deadline has expired is clearly marked for both {students_term} and {examiners_term}.'),
                        '</small></p>'
                    ],
                    data: {
                        students_term: gettext('students'),
                        examiners_term: gettext('examiners')
                    },
                    margin: '0 0 10 0'
                }, {
                    xtype: 'checkbox',
                    boxLabel: gettext('Hard deadlines'),
                    name: 'deadline_handling',
                    uncheckedValue: 0,
                    inputValue: 1
                }]
            }
        });
        this.callParent(arguments);
    }
});
