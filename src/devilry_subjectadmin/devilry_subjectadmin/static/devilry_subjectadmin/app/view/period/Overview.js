/**
 * Period overview (overview of an period).
 */
Ext.define('devilry_subjectadmin.view.period.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.periodoverview',
    cls: 'devilry_subjectadmin_periodoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_extjsextras.AlertMessage',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.ActionList',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_subjectadmin.view.BaseNodeHierLocation'
    ],

    /**
     * @cfg {String} period_id (required)
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
                xtype: 'panel',
                ui: 'transparentpanel-overflowvisible',
                layout: 'column',
                items: [{
                    xtype: 'container',
                    columnWidth: 1.0,
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
                        message: interpolate(gettext('This %(period_term)s has no students. Please go to the <a href="%(relatedstudents_url)s">manage students</a> page and add some students. You will not be able to add any assignments until you have at least one student.'), {
                            period_term: gettext('period'),
                            relatedstudents_url: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id)
                        }, true)
                    }, {
                        xtype: 'alertmessage',
                        itemId: 'noRelatedExaminersMessage',
                        hidden: true,
                        type: 'warning',
                        title: gettext('No examiners'),
                        message: interpolate(gettext('This %(period_term)s has no examiners. Please go to the <a href="%(relatedexaminers_url)s">manage examiners</a> page and add some examiners.'), {
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
                            '<h2>', gettext('Students and examiners'), '</h2>',
                            '<p class="muted">',
                                gettext('Students and examiners registered on a period are the only users available when you add students and examiners to assignments.'),
                            '</p>',
                            '<ul class="unstyled">',
                                '<li><p>',
                                    '<a href="', devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id), '">',
                                        gettext('Manage students'),
                                    '</a>',
                                '</p></li>',
                                '<li><p>',
                                    '<a href="', devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(this.period_id), '">',
                                        gettext('Manage examiners'),
                                    '</a>',
                                '</p></li>',
                            '</ul>'
                        ],
                        data: {}
                    }, {
                        xtype: 'dangerousactions',
                        margin: '20 0 0 0',
                        items: [{
                            xtype: 'singleactionbox',
                            margin: '0 0 0 0',
                            itemId: 'renameButton',
                            id: 'periodRenameButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Renaming a period should not done without a certain amount of consideration. The name of an period, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                            buttonText: gettext('Rename') + ' ...'
                        }, {
                            xtype: 'singleactionbox',
                            itemId: 'deleteButton',
                            id: 'periodDeleteButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Once you delete a period, there is no going back. Only superusers can delete a non-empty period.'),
                            buttonText: gettext('Delete') + ' ...'
                        }]
                    }]
                }, {
                    xtype: 'container',
                    border: false,
                    width: 250,
                    margin: '0 0 0 40',
                    defaults: {
                        margin: '20 0 0 0'
                    },
                    items: [{
                        xtype: 'adminsbox',
                        margin: '0 0 0 0'
                    }, {
                        xtype: 'basenodehierlocation'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
