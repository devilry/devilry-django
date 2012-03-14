/**
 * Assignment overview (overview of an assignment).
 */
Ext.define('subjectadmin.view.assignment.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentoverview',
    cls: 'assignmentoverview sidebarlayout',
    requires: [
        'Ext.layout.container.Column',
        'themebase.EditableSidebarBox',
        'subjectadmin.view.assignment.EditPublishingTimeWidget',
        'subjectadmin.view.assignment.EditAnonymousWidget',
        'subjectadmin.view.ActionList'
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
        var deleteLabel = Ext.create('Ext.XTemplate', dtranslate('themebase.delete_something')).apply({
            what: assignment
        });
        var renameLabel = Ext.create('Ext.XTemplate', dtranslate('themebase.rename_something')).apply({
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
                            url: Ext.String.format('{0}/@@manage-students', this.url),
                            text: dtranslate('subjectadmin.assignment.manage_students')
                        }, {
                            url: '#',
                            text: dtranslate('subjectadmin.assignment.manage_deadlines')
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
                        title: Ext.String.ellipsis(dtranslate('subjectadmin.assignment.waitingforfeedback'), 25),
                        columnWidth: .5,
                        margin: {right: 20},
                        html: 'TODO'
                    }, {
                        xtype: 'panel',
                        ui: 'inset-header-panel',
                        columnWidth: .5,
                        margin: {left: 20},
                        title: Ext.String.ellipsis(dtranslate('subjectadmin.assignment.upcoming_deadlines'), 25),
                        html: 'TODO'
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
                    title: dtranslate('subjectadmin.assignment.gradeeditor')
                }, {
                    xtype: 'editpublishingtime-widget',
                    disabled: true
                }, {
                    xtype: 'editanonymous-widget',
                    disabled: true
                }]
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                padding: {left: 40, top: 1, bottom: 1, right: 40},
                items: [{
                    xtype: 'button',
                    text: 'Advanced',
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
