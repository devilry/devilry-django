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
        'devilry_extjsextras.AlertMessage',
        'devilry_subjectadmin.view.assignment.GradeEditorSelectWidget',
        'devilry_subjectadmin.view.assignment.EditPublishingTimeWidget',
        'devilry_subjectadmin.view.assignment.EditAnonymousWidget',
        'devilry_subjectadmin.view.assignment.EditDeadlineHandlingWidget',
        'devilry_subjectadmin.view.DangerousActions',
        'devilry_extjsextras.SingleActionBox',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_subjectadmin.view.EditSidebarContainer',
        'devilry_subjectadmin.view.managestudents.ExaminersHelp'
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
                margin: '0 0 0 0',
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
                    tpl: [
                        '<h1 style="margin-top: 0;">{heading}</h1>'
                    ],
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
                                            gettext('Passed previously'),
                                        '</strong></a>',
                                        '<small class="muted"> - ',
                                            gettext('Wizard with automatic and manual selection.'),
                                        '</small>',
                                    '</p></li>',
                                    '<li><p>',
                                        '<strong><a href="{examinerstats_url}">',
                                            gettext('Statistics about examiners'),
                                        '</strong></a>',
                                        '<small class="muted"> - ',
                                            gettext('Charts and numbers.'),
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
                    xtype: 'container',
                    cls: 'bootstrap',
                    layout: 'fit',
                    items: {
                        xtype: 'alertmessage',
                        type: 'role-examiner',
                        itemId: 'examinerRoleBox',
                        messagetpl: [
                            '<tpl if="loading">',
                                gettext('Loading'), ' ...',
                            '<tpl else>',
                                '<tpl if="mygroupscount &gt; 0">',
                                    '<tpl if="is_published">',
                                        '<div class="pull-left" style="margin-right: 10px;">',
                                            '<a href="{examinerui_url}" target="_blank" class="btn btn-mini btn-inverse">',
                                                gettext('Go to examiner interface'),
                                                ' <i class="icon-share-alt icon-white"></i>',
                                            '</a> ',
                                        '</div>',
                                    '</tpl>',
                                    '<strong>',
                                        gettext('You are examiner for {mygroupscount}/{totalgroups} groups.'),
                                    '</strong>',
                                    ' ',
                                    '<tpl if="!is_published">',
                                        '<small>',
                                            gettext('When this assignment is published, you will get a link here that takes you to the examiner interface.'),
                                        '</small>',
                                    '</tpl>',
                                '<tpl else>',
                                    gettext('You are not examiner for any groups on this assignment.'),
                                '</tpl>',
                                ' <small>{MORE_BUTTON}</small>',
                                '<div {MORE_ATTRS}>',
                                    '<p style="margin-top:10px;">',
                                        gettext('Follow the Students-link above if you wish to manage examiners.'),
                                    '</p>',
                                    '<h4>',
                                        gettext('About examiners'),
                                    '</h4>',
                                    '<p>',
                                        devilry_subjectadmin.view.managestudents.ExaminersHelp.getIntroText(),
                                    '</p>',
                                    devilry_subjectadmin.view.managestudents.ExaminersHelp.getDetailsUl(),
                                '</div>',
                            '</tpl>'
                        ],
                        messagedata: {
                            loading: true
                        }
                    }
                }, {
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
                }, {
                    xtype: 'dangerousactions',
                    title: gettext('Beta features'),
                    margin: '30 0 0 0',
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap devilry_subjectadmin_navigation',
                        itemId: 'betaFeaturesBox',
                        tpl: [
                            '<tpl if="loading">',
                                '<p class="muted">', gettext('Loading'), '...</p>',
                            '<tpl else>',
                                '<ul class="unstyled">',
                                    '<li><p>',
                                        '<strong><a href="{detektor_assemblyview_url}">',
                                            gettext('Programming code similarity checks'),
                                        '</strong></a>',
                                        '<small class="muted"> - ',
                                            gettext('Run similarity checks for all deliveries on this assignment.'),
                                        '</small>',
                                    '</p></li>',
                                    '<p><li>',
                                        '<strong>',
                                            '<a href="{downloaddeliveries_url}">',
                                                '<i class="fa fa-download"></i>',
                                                gettext('Download all deliveries'),
                                            '</a>',
                                        '</strong>',
                                        '<small class="muted"> - ',
                                            gettext('As zip-file'),
                                        '</small>',
                                    '</p></li>',
                                '</ul>',
                            '</tpl>'
                        ],
                        data: {
                            loading: true,
                            downloaddeliveries_url: ''
                        }
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
