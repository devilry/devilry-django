/**
 * A panel that displays information about a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.SingleGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'devilry_subjectadmin_singlegroupview',
    autoScroll: true,
    border: 0,
    bodyPadding: 20,

    requires: [
        'devilry_subjectadmin.view.managestudents.ManageStudentsOnSingle',
        'devilry_subjectadmin.view.managestudents.ManageExaminersOnSingle',
        'devilry_subjectadmin.view.managestudents.ManageTagsOnSingle',
        'devilry_subjectadmin.view.managestudents.SingleMetaInfo',
        'devilry_subjectadmin.view.DangerousActions',
        'devilry_extjsextras.SingleActionBox',
        'devilry_extjsextras.AlertMessageList'
    ],

    /**
     * @cfg {String} [assignment_id]
     */

    /**
     * @cfg {devilry_subjectadmin.model.Group} groupRecord (required)
     */

    /**
     * @cfg {Ext.data.Store} studentsStore (required)
     */

    /**
     * @cfg {Ext.data.Store} examinersStore (required)
     */

    /**
     * @cfg {Ext.data.Store} tagsStore (required)
     */

    /**
     * @cfg {int} [period_id]
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'container',
                anchor: '100%',
                layout: 'anchor',
                items: [{
                    xtype: 'container',
                    layout: 'anchor',
                    defaults: {
                        anchor: '100%'
                    },
                    columnWidth: 1,
                    items: [{
                        xtype: 'singlegroupmetainfo',
                        groupRecord: this.groupRecord,
                        assignment_id: this.assignment_id
                    }]
                }, {
                    xtype: 'container',
                    padding: '0 0 0 0',
                    margin: '20 0 0 0',
                    layout: 'column',
                    items: [{
                        xtype: 'managestudentsonsingle',
                        columnWidth: 0.30,
                        margin: '0 10 0 0',
                        studentsStore: this.studentsStore
                    }, {
                        xtype: 'managetagsonsingle',
                        columnWidth: 0.30,
                        margin: '0 5 0 5',
                        tagsStore: this.tagsStore
                    }, {
                        xtype: 'manageexaminersonsingle',
                        examinersStore: this.examinersStore,
                        margin: '0 0 0 10',
                        columnWidth: 0.40,
                        period_id: this.period_id
                    }]
                }]
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                itemId: 'header',
                tpl: '<h3>{heading}</h3>',
                data: {
                    heading: gettext('Deadlines and deliveries')
                }
            }, {
                xtype: 'admingroupinfo_deadlinescontainer'
            }, {
                xtype: 'alertmessagelist',
                margin: '20 0 0 0',
                itemId: 'examinerRoleList',
                cls: 'examinerRoleList'
            }, {
                xtype: 'dangerousactions',
                margin: '20 0 0 0',
                titleTpl: '<h3>{heading}</h3>',
                items: [{
                    xtype: 'singleactionbox',
                    itemId: 'deleteButton',
                    id: 'single_group_delete_button',
                    titleText: gettext('Delete'),
                    bodyHtml: interpolate(gettext('Once you delete a %(group_term)s, there is no going back. Only superusers can delete a %(group_term)s with deliveries.'), {
                        group_term: gettext('group')
                    }, true),
                    buttonText: gettext('Delete') + ' ...',
                    buttonUi: 'danger'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
