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
                        margin: '40 0 0 0',
                        itemId: 'dangerousactions',
                        ui: 'inset-header-danger-panel',
                        title: gettext('Dangerous actions'),
                        layout: 'anchor',
                        defaults: {
                            anchor: '100%',
                            margin: '10 0 0 0'
                        },
                        items: [{
                            xtype: 'singleactionbox',
                            margin: '0 0 0 0',
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
                    margin: '0 0 0 40',
                    defaults: {
                        margin: '20 0 0 0',
                    },
                    items: [{
                        xtype: 'adminsbox',
                        margin: '0 0 0 0'
                    }, {
                        xtype: 'basenodehierlocation'
                    }]
                }],
            }]
        });
        this.callParent(arguments);
    }
});
