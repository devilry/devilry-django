/**
 * Assignment overview (overview of an assignment).
 */
Ext.define('devilry_subjectadmin.view.assignment.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentoverview',
    cls: 'assignmentoverview sidebarlayout',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_subjectadmin.view.assignment.EditPublishingTimeWidget',
        'devilry_subjectadmin.view.assignment.EditAnonymousWidget',
        'devilry_subjectadmin.view.ActionList'
    ],


    /**
     * @cfg {String} url (required)
     */

    /**
     * @cfg {String} subject_shortname (required)
     */

    /**
     * @cfg {String} period_shortname (required)
     */

    /**
     * @cfg {String} assignment_shortname (required)
     */


    initComponent: function() {
        var assignment = Ext.String.format('{0}.{1}.{2}',
            this.subject_shortname, this.period_shortname,
            this.assignment_shortname
        );
        var deleteLabel = Ext.create('Ext.XTemplate', dtranslate('devilry_extjsextras.delete_something')).apply({
            what: assignment
        });
        var renameLabel = Ext.create('Ext.XTemplate', dtranslate('devilry_extjsextras.rename_something')).apply({
            what: assignment
        });


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
                    items: {
                        xtype: 'actionlist',
                        links: [{
                            url: Ext.String.format('{0}@@manage-students', this.url),
                            text: dtranslate('devilry_subjectadmin.assignment.manage_students')
                        }, {
                            url: Ext.String.format('{0}@@manage-deadlines', this.url),
                            text: dtranslate('devilry_subjectadmin.assignment.manage_deadlines')
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
                        title: Ext.String.ellipsis(dtranslate('devilry_subjectadmin.assignment.upcoming_deadlines'), 25),
                        html: 'TODO. See this <a href="http://heim.ifi.uio.no/espeak/devilry-figures/assignmentadmin.png" target="_blank">mockup image</a>.'
                    }, {
                        xtype: 'panel',
                        ui: 'inset-header-panel',
                        title: Ext.String.ellipsis(dtranslate('devilry_subjectadmin.assignment.waitingforfeedback'), 25),
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
                    title: dtranslate('devilry_subjectadmin.assignment.gradeeditor')
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
