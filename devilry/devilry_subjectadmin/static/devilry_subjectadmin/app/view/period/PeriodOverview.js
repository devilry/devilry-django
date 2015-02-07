/**
 * Period overview (overview of an period).
 */
Ext.define('devilry_subjectadmin.view.period.PeriodOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.periodoverview',
    cls: 'devilry_subjectadmin_periodoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.AlertMessage',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_subjectadmin.view.DangerousActions',
        'devilry_subjectadmin.view.period.EditDurationWidget',
        'devilry_extjsextras.SingleActionBox',
        'devilry_subjectadmin.view.EditSidebarContainer'
    ],

    /**
     * @cfg {String} period_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            padding: '20 20 20 20',
            autoScroll: true,
            layout: 'column',

            items: [{
                xtype: 'editsidebarcontainer',
                layout: 'anchor',
                width: 250,
                margin: '0 0 0 0',
                padding: '0 10 0 10',
                defaults: {
                    margin: '10 0 0 0',
                    anchor: '100%'
                },
                items: [{
                    //margin: '0 0 0 0',
                    xtype: 'editperiod_duration-widget'
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
                        '<tpl if="loading">',
                            gettext('Loading'), ' ...',
                        '<tpl else>',
                            '<h1 style="margin-top: 0;">',
                                '{period}',
                                ' <small class="muted"> &mdash; {subject}</small>',
                            '</h1>',
                        '</tpl>'
                    ],
                    data: {
                        loading: true
                    }
                }, {
                    xtype: 'box',
                    cls: 'bootstrap devilry_subjectadmin_navigation',
                    itemId: 'createNewAssignmentBox',
                    tpl: [
                        '<p><strong><a href="{url}">{text}</a></strong></p>'
                    ],
                    data: {
                        url: devilry_subjectadmin.utils.UrlLookup.createNewAssignment(this.period_id),
                        text: gettext('Create new assignment')
                    }
                }, {
                    xtype: 'alertmessage',
                    itemId: 'noRelatedStudentsMessage',
                    hidden: true,
                    type: 'error',
                    title: gettext('No students'),
                    message: interpolate(gettext('This %(period_term)s has no students. Go to the <a href="%(relatedstudents_url)s">students</a> page and add some students. You will not be able to add any assignments until you have at least one student.'), {
                        period_term: gettext('period'),
                        relatedstudents_url: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id)
                    }, true)
                }, {
                    xtype: 'alertmessage',
                    itemId: 'noRelatedExaminersMessage',
                    hidden: true,
                    type: 'warning',
                    title: gettext('No examiners'),
                    message: interpolate(gettext('This %(period_term)s has no examiners. Go to the <a href="%(relatedexaminers_url)s">examiners</a> page and add some examiners.'), {
                        period_term: gettext('period'),
                        relatedexaminers_url: devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(this.period_id)
                    }, true)
                }, {
                    xtype: 'listofassignments'
                }, {
                    xtype: 'box',
                    cls: 'bootstrap',
                    margin: '30 0 0 0',
                    tpl: [
                        '<h3>',
                            gettext('Edit and view related information'),
                        '</h3>',
                        '<ul class="unstyled">',
                            '<li><p>',
                                '<a href="{manageRelatedStudentsUrl}">',
                                    gettext('Students'),
                                '</a>',
                            '</p></li>',
                            '<li><p>',
                                '<a href="{manageRelatedExaminersUrl}">',
                                    gettext('Examiners'),
                                '</a>',
                            '</p></li>',
                            '<li><p>',
                                '<a href="{detailedOverviewUlr}">',
                                    gettext('Overview of all results'),
                                '</a>',
                            '</p></li>',
                           '<li><p>',
                               '<a href="{qualifiedForFinalExamsUrl}" class="qualifiedforfinalexams">',
                                   gettext('Qualified for final exams'),
                               '</a>',
                           '</p></li>',
                        '</ul>'
                    ],
                    data: {
                        period_term: gettext('period'),
                        manageRelatedExaminersUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(this.period_id),
                        manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id),
                        detailedOverviewUlr: devilry_subjectadmin.utils.UrlLookup.detailedPeriodOverview(this.period_id),
                        qualifiedForFinalExamsUrl: Ext.String.format(
                            '{0}/devilry_qualifiesforexam/#/{1}/showstatus',
                            window.DevilrySettings.DEVILRY_URLPATH_PREFIX,
                            this.period_id)
                    }
                }, {
                    xtype: 'dangerousactions',
                    margin: '45 0 0 0',
                    items: [{
                        xtype: 'singleactionbox',
                        margin: '0 0 0 0',
                        itemId: 'renameButton',
                        id: 'periodRenameButton',
                        titleText: gettext('Loading') + ' ...',
                        bodyTpl: [
                            '<p class="muted"><small>',
                                gettext('Renaming a {period_term} should not be done without a certain amount of consideration. The name of a {period_term}, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                            '</small></p>'
                        ],
                        bodyData: {
                            period_term: gettext('period')
                        },
                        buttonText: gettext('Rename') + ' ...'
                    }, {
                        xtype: 'singleactionbox',
                        itemId: 'deleteButton',
                        id: 'periodDeleteButton',
                        hidden: true,
                        titleText: gettext('Loading') + ' ...',
                        buttonUi: 'danger',
                        bodyTpl: [
                            '<p class="muted"><small>',
                                gettext('Once you delete a {period_term}, there is no going back. Only superusers can delete a non-empty {period_term}.'),
                            '</small></p>'
                        ],
                        bodyData: {
                            period_term: gettext('period')
                        },
                        buttonText: gettext('Delete') + ' ...'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
