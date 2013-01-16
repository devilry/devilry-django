/**
 * Assignment overview (overview of an assignment).
 */
Ext.define('devilry_subjectadmin.view.assignment.AssignmentOverview' ,{
    extend: 'Ext.container.Container',
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
        'devilry_subjectadmin.view.DangerousActions',
        'devilry_extjsextras.SingleActionBox',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_subjectadmin.view.EditSidebarContainer'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            padding: '20 20 20 20',
            autoScroll: true,
            layout: 'column',

            items: [{
                xtype: 'editsidebarcontainer',
                width: 250,
                margin: '6 0 0 0',
                padding: '0 10 0 10',
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
                    xtype: 'adminsbox'
                }]
            }, {
                xtype: 'container',
                columnWidth: 1.0,
                cls: 'devilry_focuscontainer',
                padding: '20',
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    margin: '0 0 20 0',
                    itemId: 'header',
                    tpl: '<h1 style="margin-top: 0;">{heading}</h1>',
                    data: {
                        heading: gettext('Loading') + ' ...'
                    }
                }, {
                    xtype: 'alertmessage',
                    itemId: 'noGroupsMessage',
                    hidden: true,
                    type: 'warning',
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
                            '<tpl if="has_students">',
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
                                    '<tpl if="electronic">',
                                        '<li><p>',
                                            '<strong><a href="{managedeadlines_url}">',
                                                gettext('Deadlines'),
                                            '</a></strong>',
                                            '<small class="muted"> - ',
                                                gettext('View, edit and add deadlines, including the submission date.'),
                                            '</small>',
                                        '</p></li>',
                                    '</tpl>',
                                    '<li><p>',
                                        '<strong><a href="{passedpreviousperiod_url}">',
                                            gettext('Passed previous {period_term}'),
                                        '</strong></a>',
                                        '<small class="muted"> - ',
                                            gettext('Wizard with automatic and manual selection.'),
                                        '</small>',
                                    '</p></li>',
                                '</ul>',
                            '</tpl>',
                        '</tpl>'
                    ],
                    data: {
                        loading: true
                    }
                }, {
                    //xtype: 'box',
                    //cls: 'bootstrap tools',
                    //itemId: 'linkList',
                    //tpl: [
                        //'<h2'
                    //],
                    //data: {}
                //}, {
                    xtype: 'dangerousactions',
                    margin: '125 0 0 0',
                    items: [{
                        xtype: 'singleactionbox',
                        margin: 0,
                        itemId: 'renameButton',
                        id: 'assignmentRenameButton',
                        titleText: gettext('Loading') + ' ...',
                        bodyHtml: [
                            '<small>',
                                gettext('Renaming an assignment should not be done without a certain amount of consideration. The name of an assignment, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                            '</small>'
                        ].join(''),
                        buttonText: gettext('Rename') + ' ...'
                    }, {
                        xtype: 'singleactionbox',
                        itemId: 'deleteButton',
                        hidden: true,
                        id: 'assignmentDeleteButton',
                        titleText: gettext('Loading') + ' ...',
                        bodyHtml: [
                            '<small>',
                                gettext('Once you delete an assignment, there is no going back. Only superusers can delete an assignment with deliveries.'),
                            '</small>'
                        ].join(''),
                        buttonText: gettext('Delete') + ' ...',
                        buttonUi: 'danger'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
