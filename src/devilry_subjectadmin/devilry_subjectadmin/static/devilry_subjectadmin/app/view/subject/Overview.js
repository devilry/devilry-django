/**
 * Subject overview (overview of an subject).
 */
Ext.define('devilry_subjectadmin.view.subject.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.subjectoverview',
    cls: 'devilry_subjectoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_subjectadmin.view.ActionList',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_extjsextras.SingleActionBox',
        'devilry_subjectadmin.view.BaseNodeHierLocation'
    ],


    /**
     * @cfg {String} subject_id (required)
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
                    columnWidth: .65,
                    items: [{
                        xtype: 'panel',
                        itemId: 'actions',
                        ui: 'inset-header-strong-panel',
                        layout: 'fit',
                        items: {
                            xtype: 'listofperiods'
                        }
                    }, {
                        xtype: 'panel',
                        margin: {top: 40},
                        itemId: 'dangerousactions',
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
                            id: 'subjectRenameButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Renaming a subject should not done without a certain amount of consideration. The name of a subject, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                            buttonText: gettext('Rename') + ' ...'
                        }, {
                            xtype: 'singleactionbox',
                            itemId: 'deleteButton',
                            id: 'subjectDeleteButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Once you delete a subject, there is no going back. Only superusers can delete a non-empty subject.'),
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
