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
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.ActionList',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_subjectadmin.view.period.OverviewOfRelatedUsers',
        'devilry_subjectadmin.view.BaseNodeHierLocation'
    ],

    /**
     * @cfg {String} period_id (required)
     */


    initComponent: function() {
        var deleteLabel = gettext('Loading ...');
        var renameLabel = gettext('Loading ...');

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
                    columnWidth: .65,
                    items: [{
                        xtype: 'panel',
                        itemId: 'actions',
                        ui: 'inset-header-strong-panel',
                        layout: 'fit',
                        items: {
                            xtype: 'listofassignments'
                        }
                    }, {
                        xtype: 'panel',
                        itemId: 'relatedusers',
                        margin: {top: 40},
                        ui: 'inset-header-panel',
                        title: gettext('Students and examiners on this period'),
                        layout: 'fit',
                        items: {
                            xtype: 'overviewofrelatedusers'
                        }
                    }, {
                        xtype: 'panel',
                        itemId: 'dangerousactions',
                        margin: {top: 40},
                        ui: 'inset-header-danger-panel',
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
                    columnWidth: .35,
                    margin: {left: 40},
                    defaults: {
                        margin: {top: 20},
                    },
                    items: [{
                        xtype: 'adminsbox',
                        margin: {top: 0}
                    }, {
                        xtype: 'basenodehierlocation'
                    }]
                }],
            }]
        });
        this.callParent(arguments);
    }
});
