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
     * @cfg {int} [period_id]
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'singlegroupmetainfo'
            }, {
                xtype: 'container',
                padding: '0 0 0 0',
                margin: '10 0 0 0',
                layout: 'column',
                items: [{
                    xtype: 'managestudentsonsingle',
                    columnWidth: 0.30,
                    margin: '0 10 0 0'
                }, {
                    xtype: 'managetagsonsingle',
                    columnWidth: 0.30,
                    margin: '0 5 0 5'
                }, {
                    xtype: 'manageexaminersonsingle',
                    margin: '0 0 0 10',
                    columnWidth: 0.40,
                    period_id: this.period_id
                }]
            }, {
                xtype: 'alertmessagelist',
                margin: '20 0 0 0',
                itemId: 'examinerRoleList',
                cls: 'examinerRoleList'
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                itemId: 'header',
                margin: '20 0 0 0',
                tpl: '<h3 class="muted">{heading}</h3>',
                data: {
                    heading: gettext('Deadlines, deliveries and feedback')
                }
            }, {
                xtype: 'admingroupinfo_deadlinescontainer'
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
