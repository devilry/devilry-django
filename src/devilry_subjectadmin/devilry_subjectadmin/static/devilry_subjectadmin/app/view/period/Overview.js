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
                        xtype: 'box',
                        cls: 'bootstrap',
                        margin: '0 0 20 0',
                        itemId: 'header',
                        tpl: '<h1>{heading}</h1>',
                        data: {
                            heading: gettext('Loading') + ' ...'
                        }
                    }, {
                        xtype: 'listofassignments'
                    }, {
                        xtype: 'box',
                        cls: 'bootstrap',
                        margin: '40 0 0 0',
                        tpl: '<h2>{heading}</h2>',
                        data: {
                            heading: interpolate(gettext('Students and examiners'), {
                                Students_term: gettext('Students'),
                                examiners_term: gettext('examiners')
                            }, true)
                        }
                    }, {
                        xtype: 'overviewofrelatedusers'
                    }, {
                        xtype: 'panel',
                        itemId: 'dangerousactions',
                        margin: '40 0 0 0',
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
                    margin: '0 0 0 40',
                    defaults: {
                        margin: '20 0 0 0'
                    },
                    items: [{
                        xtype: 'adminsbox',
                        margin: '0 0 0 0'
                    }, {
                        xtype: 'basenodehierlocation'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
