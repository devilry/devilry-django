/**
 * Assignment overview (overview of an assignment).
 */
Ext.define('subjectadmin.view.assignment.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentoverview',
    cls: 'assignmentoverview sidebarlayout',
    requires: [
        'Ext.layout.container.Column',
        'themebase.layout.RightSidebar',
        'themebase.CenterTitle',
        'themebase.EditableSidebarBox',
        'subjectadmin.view.assignment.EditPublishingTimeWidget',
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
                            text: dtranslate('subjectadmin.assignment.manage-students')
                        }, {
                            url: '#',
                            text: dtranslate('subjectadmin.assignment.manage-deadlines')
                        }, {
                            url: '#',
                            buttonType: 'danger',
                            text: dtranslate('themebase.delete-something')
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
                        title: Ext.String.ellipsis(dtranslate('subjectadmin.assignment.upcoming-deadlines'), 25),
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
                }]
            }]
        });
        this.callParent(arguments);
    }
});
