/**
 * Period overview (overview of an period).
 */
Ext.define('devilry_subjectadmin.view.period.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.periodoverview',
    cls: 'periodoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.ActionList'
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
                    id: 'menubarAdvancedButton',
                    text: gettext('Advanced'),
                    scale: 'medium',
                    menu: [{
                        itemId: 'renameButton',
                        id: 'menubarAdvancedRenameButton',
                        text: renameLabel
                    }, {
                        itemId: 'deleteButton',
                        id: 'menubarAdvancedDeleteButton',
                        text: deleteLabel
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
