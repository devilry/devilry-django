/**
 * Subject overview (overview of an subject).
 */
Ext.define('devilry_subjectadmin.view.subject.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.subjectoverview',
    cls: 'devilry_subjectoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_subjectadmin.view.ActionList',
        'devilry_extjsextras.AlertMessageList'
    ],


    /**
     * @cfg {String} subject_id (required)
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
                            xtype: 'listofperiods'
                        }
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
                        margin: {top: 0},
                        itemId: 'admins',
                        title: gettext('Administrators')
                    }]
                }],
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                padding: {left: 40, top: 1, bottom: 1, right: 40},
                items: [{
                    xtype: 'button',
                    text: gettext('Advanced'),
                    scale: 'medium',
                    menu: [{
                        itemId: 'renameButton',
                        text: renameLabel
                    }, {
                        itemId: 'deleteButton',
                        text: deleteLabel
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
