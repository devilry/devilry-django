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
        var periodpath = Ext.String.format('{0}.{1}', this.subject_shortname, this.period_shortname);
        var deleteLabel = Ext.create('Ext.XTemplate', dtranslate('devilry_extjsextras.delete_something')).apply({
            what: this.periodpath
        });
        var renameLabel = Ext.create('Ext.XTemplate', dtranslate('devilry_extjsextras.rename_something')).apply({
            what: this.periodpath
        });


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
                        title: dtranslate('devilry_subjectadmin.administrators')
                    }]
                }],
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                padding: {left: 40, top: 1, bottom: 1, right: 40},
                items: [{
                    xtype: 'button',
                    text: dtranslate('devilry_extjsextras.advanced'),
                    scale: 'medium',
                    menu: [{
                        text: renameLabel,
                        listeners: {
                            scope: this,
                            click: this._notImplemented
                        }
                    }, {
                        text: deleteLabel,
                        listeners: {
                            scope: this,
                            click: this._notImplemented
                        }
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    _notImplemented: function() {
        Ext.MessageBox.alert('Unavailable', 'Not implemented yet');
    }
});
