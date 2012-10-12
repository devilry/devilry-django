/**
 * Assignment overview (overview of an assignment).
 */
Ext.define('devilry_subjectadmin.view.assignment.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentoverview',
    cls: 'devilry_subjectadmin_assignmentoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.assignment.GradeEditorSelectWidget',
        'devilry_subjectadmin.view.assignment.EditPublishingTimeWidget',
        'devilry_subjectadmin.view.assignment.EditAnonymousWidget',
        'devilry_subjectadmin.view.assignment.EditDeadlineHandlingWidget',
        'devilry_subjectadmin.view.assignment.EditFirstDeadlineWidget',
        'devilry_subjectadmin.view.DangerousActions',
        'devilry_extjsextras.SingleActionBox',
        'devilry_subjectadmin.view.AdminsBox'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            frame: false,
            border: 0,
            bodyPadding: 40,
            autoScroll: true,

            items: [{
                xtype: 'alertmessagelist'
            }, {
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'container',
                    columnWidth: 1,
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap',
                        margin: '0 0 20 0',
                        itemId: 'header',
                        tpl: '<h1>{heading}</h1>',
                        data: {
                            heading: gettext('Loading') + ' ...'
                        }
                    }, {
                        xtype: 'alertmessage',
                        itemId: 'noGroupsMessage',
                        hidden: true,
                        type: 'error',
                        title: gettext('No students'),
                        message: interpolate(gettext('This assignment has no students. You need to <a href="%(addstudents_url)s">add students</a>.'), {
                            addstudents_url: devilry_subjectadmin.utils.UrlLookup.manageStudentsAddStudents(this.assignment_id)
                        }, true)
                    }, {
                        xtype: 'box',
                        cls: 'bootstrap devilry_subjectadmin_navigation',
                        itemId: 'linkList',
                        tpl: [
                            '<tpl if="loading">',
                                '<p class="muted">', gettext('Loading'), '...</p>',
                            '<tpl else>',
                                '<ul class="unstyled">',
                                    '<li><p>',
                                        '<strong><a href="{managestudents_url}">',
                                            gettext('Students'),
                                        '</a></strong>',
                                        '<small class="muted"> - ',
                                            gettext('View, edit and add students on this assignment'),
                                            ' (',
                                                '<em>', gettext('Students'),   ':</em> {assignmentData.number_of_candidates}, ',
                                                '<em>', gettext('Groups'),     ':</em> {assignmentData.number_of_groups}, ',
                                                '<em>', gettext('Deliveries'), ':</em> {assignmentData.number_of_deliveries}',
                                            ').',
                                        '</small>',
                                    '</p></li>',
                                    '<li><p>',
                                        '<strong><a href="{managedeadlines_url}">',
                                            gettext('Deadlines'),
                                        '</a></strong>',
                                        '<small class="muted"> - ',
                                            gettext('View, edit and add deadlines.'),
                                        '</small>',
                                    '</p></li>',
                                '</ul>',
                            '</tpl>'
                        ],
                        data: {
                            loading: true
                        }
                    }, {
                        xtype: 'dangerousactions',
                        margin: '20 0 0 0',
                        items: [{
                            xtype: 'singleactionbox',
                            margin: 0,
                            itemId: 'renameButton',
                            id: 'assignmentRenameButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Renaming an assignment should not done without a certain amount of consideration. The name of an assignment, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                            buttonText: gettext('Rename') + ' ...'
                        }, {
                            xtype: 'singleactionbox',
                            itemId: 'deleteButton',
                            id: 'assignmentDeleteButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Once you delete an assignment, there is no going back. Only superusers can delete an assignment with deliveries.'),
                            buttonText: gettext('Delete') + ' ...',
                            buttonUi: 'danger'
                        }]
                    }]
                }, {
                    xtype: 'container',
                    border: false,
                    width: 250,
                    margin: '6 0 0 40',
                    defaults: {
                        margin: '10 0 0 0'
                    },
                    items: [{
                        xtype: 'gradeeditorselect-widget',
                        disabled: true
                    }, {
                        xtype: 'editpublishingtime-widget'
                    }, {
                        xtype: 'editanonymous-widget'
                    }, {
                        xtype: 'editdeadline_handling-widget'
                    }, {
                        xtype: 'editfirstdeadline-widget'
                    }, {
                        xtype: 'adminsbox'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
