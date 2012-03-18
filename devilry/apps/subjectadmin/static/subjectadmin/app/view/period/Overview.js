/**
 * Period overview (overview of an period).
 */
Ext.define('subjectadmin.view.period.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.periodoverview',
    cls: 'periodoverview',
    requires: [
        'Ext.layout.container.Column',
        'themebase.EditableSidebarBox',
        'themebase.AlertMessageList',
        'subjectadmin.view.ActionList'
    ],

    /**
     * @cfg {String} subject_shortname (required)
     */

    /**
     * @cfg {String} period_shortname (required)
     */


    initComponent: function() {
        var periodpath = Ext.String.format('{0}.{1}', this.subject_shortname, this.period_shortname);
        var deleteLabel = Ext.create('Ext.XTemplate', dtranslate('themebase.delete_something')).apply({
            what: this.periodpath
        });
        var renameLabel = Ext.create('Ext.XTemplate', dtranslate('themebase.rename_something')).apply({
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
                        html: 'list of assignments...'
                        //items: {
                            //xtype: 'listofassignments'
                        //}
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
                        title: dtranslate('subjectadmin.administrators')
                    }]
                }],
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                padding: {left: 40, top: 1, bottom: 1, right: 40},
                items: [{
                    xtype: 'button',
                    text: dtranslate('themebase.advanced'),
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
