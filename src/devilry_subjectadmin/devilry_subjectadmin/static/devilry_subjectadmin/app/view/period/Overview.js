/**
 * Period overview (overview of an period).
 */
Ext.define('devilry_subjectadmin.view.period.Overview' ,{
    extend: 'Ext.panel.Panel',
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
        'devilry_extjsextras.SingleActionBox'
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
                frame: false,
                border: false,
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
                        message: interpolate(gettext('This %(period_term)s has no students. Go to the <a href="%(relatedstudents_url)s">manage related students</a> page and add some students. You will not be able to add any assignments until you have at least one student.'), {
                            period_term: gettext('period'),
                            relatedstudents_url: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id)
                        }, true)
                    }, {
                        xtype: 'alertmessage',
                        itemId: 'noRelatedExaminersMessage',
                        hidden: true,
                        type: 'warning',
                        title: gettext('No examiners'),
                        message: interpolate(gettext('This %(period_term)s has no examiners. Go to the <a href="%(relatedexaminers_url)s">manage related examiners</a> page and add some examiners.'), {
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
                            '<h2>', gettext('{Students_term} and examiners'), '</h2>',
                            '<ul class="unstyled">',
                                '<li><p>',
                                    '<a href="', devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id), '">',
                                        '{Students_term}',
                                    '</a>',
                                '</p></li>',
                                '<li><p>',
                                    '<a href="', devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(this.period_id), '">',
                                        gettext('Examiners'),
                                    '</a>',
                                '</p></li>',
                            '</ul>'
                        ],
                        data: {
                            Students_term: gettext('Students')
                        }
                    }, {
                        xtype: 'dangerousactions',
                        margin: '20 0 0 0',
                        items: [{
                            xtype: 'singleactionbox',
                            margin: '0 0 0 0',
                            itemId: 'renameButton',
                            id: 'periodRenameButton',
                            titleText: gettext('Loading ...'),
                            bodyTpl: [
                                '<p class="muted">',
                                    gettext('Renaming a {period_term} should not done without a certain amount of consideration. The name of a {period_term}, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                                '</p>'
                            ],
                            bodyData: {
                                period_term: gettext('period')
                            },
                            buttonText: gettext('Rename') + ' ...'
                        }, {
                            xtype: 'singleactionbox',
                            itemId: 'deleteButton',
                            id: 'periodDeleteButton',
                            titleText: gettext('Loading ...'),
                            buttonUi: 'danger',
                            bodyTpl: [
                                '<p class="muted">',
                                    gettext('Once you delete a {period_term}, there is no going back. Only superusers can delete a non-empty {period_term}.'),
                                '</p>'
                            ],
                            bodyData: {
                                period_term: gettext('period')
                            },
                            buttonText: gettext('Delete') + ' ...'
                        }]
                    }]
                }, {
                    xtype: 'container',
                    border: false,
                    width: 250,
                    margin: '6 0 0 40',
                    layout: 'anchor',
                    defaults: {
                        margin: '20 0 0 0',
                        anchor: '100%'
                    },
                    items: [{
                        margin: '0 0 0 0',
                        xtype: 'editperiod_duration-widget'
                    }, {
                        xtype: 'adminsbox'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
