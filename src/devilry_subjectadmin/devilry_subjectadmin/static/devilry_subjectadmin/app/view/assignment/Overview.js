/**
 * Assignment overview (overview of an assignment).
 */
Ext.define('devilry_subjectadmin.view.assignment.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentoverview',
    cls: 'assignmentoverview sidebarlayout',
    requires: [
        'Ext.layout.container.Column',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_subjectadmin.view.assignment.EditPublishingTimeWidget',
        'devilry_subjectadmin.view.assignment.EditAnonymousWidget',
        'devilry_subjectadmin.view.ActionList'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'column',
            frame: false,
            border: 0,
            bodyPadding: 40,
            autoScroll: true,

            items: [{
                xtype: 'container',
                columnWidth: .65,
                items: [{
                    xtype: 'panel',
                    itemId: 'actions',
                    ui: 'inset-header-strong-panel',
                    title: gettext('Loading ...'),
                    items: {
                        xtype: 'actionlist',
                        links: [{
                            url: devilry_subjectadmin.utils.UrlLookup.manageStudents(this.assignment_id),
                            text: gettext('Manage students')
                        }, {
                            url: devilry_subjectadmin.utils.UrlLookup.manageDeadlines(this.assignment_id),
                            text: gettext('Manage deadlines')
                        }]
                    }
                }, {
                    xtype: 'panel',
                    ui: 'transparentpanel-overflowvisible',
                    margin: {top: 40},
                    layout: 'column',
                    items: [{
                        xtype: 'panel',
                        ui: 'inset-header-panel',
                        margin: {right: 20},
                        columnWidth: .5,
                        title: gettext('Upcoming deadlines'),
                        html: 'TODO. See this <a href="http://heim.ifi.uio.no/espeak/devilry-figures/assignmentadmin.png" target="_blank">mockup image</a>.'
                    }, {
                        xtype: 'panel',
                        ui: 'inset-header-panel',
                        title: gettext('Waiting for feedback'),
                        columnWidth: .5,
                        margin: {left: 20},
                        html: 'TODO. See this <a href="http://heim.ifi.uio.no/espeak/devilry-figures/assignmentadmin.png" target="_blank">mockup image</a>.'
                    }]
                }, {
                    xtype: 'panel',
                    margin: {top: 40},
                    itemId: 'dangerousactions',
                    ui: 'inset-header-panel',
                    title: gettext('Dangerous actions'),
                    layout: 'anchor',
                    defaults: {
                        anchor: '100%',
                        margin: {top: 10}
                    },
                    items: [{
                        xtype: 'singleactionbox',
                        margin: {top: 0},
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
                        bodyHtml: gettext('Once you delete an assignment, there is no going back. Only superusers can delete a non-empty assignment.'),
                        buttonText: gettext('Delete') + ' ...'
                    }]
                }]
            }, {
                xtype: 'container',
                border: false,
                columnWidth: .35,
                margin: {left: 40},
                defaults: {
                    margin: {top: 20},
                },
                items: [{
                    xtype: 'editablesidebarbox',
                    itemId: 'gradeeditor',
                    margin: {top: 0},
                    title: gettext('Grade editor')
                }, {
                    xtype: 'editpublishingtime-widget',
                    disabled: true
                }, {
                    xtype: 'editanonymous-widget',
                    disabled: true
                }]
            }]
        });
        this.callParent(arguments);
    }
});
