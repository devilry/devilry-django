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
        'devilry_subjectadmin.view.managestudents.ExaminersHelp',
        'devilry_extjsextras.SingleActionBox',
        'devilry_extjsextras.AlertMessageList'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'alertmessage',
                type: 'role-examiner',
                cls: 'examinerRoleBox',
                extracls: 'flat compact',
                itemId: 'examinerRoleBox',
                margin: '-20 -20 20 -20',
                messagetpl: [
                    '<tpl if="loading">',
                        '<p><small>',
                            gettext('Loading'), ' ...',
                        '</small></p>',
                    '<tpl else>',
                        '<div style="padding-left: 13px">', // Pad to line up with the rest of the view
                            '<tpl if="is_published">',
                                '<div class="pull-left" style="margin-right: 10px;">',
                                    '<tpl if="isExaminer">',
                                        ' <a href="{examinerui_url}" target="_blank" class="btn btn-mini btn-inverse">',
                                            gettext('Create/edit feedback'),
                                            ' <i class="icon-share-alt icon-white"></i>',
                                        '</a>',
                                    '<tpl else>',
                                        ' <a href="{make_examiner}" class="btn btn-mini btn-inverse make_me_examiner">',
                                            gettext('Make me examiner'),
                                        '</a>',
                                    '</tpl>',
                                '</div>',
                                '<div class="text" style="display:block; padding-top: 2px;">', // Style to align text with button
                                    '<small>',
                                        '<tpl if="isExaminer">',
                                            gettext('You are examiner for this group.'),
                                        '<tpl else>',
                                            gettext('You need to be examiner for this group if you want to provide feedback.'),
                                        '</tpl>',
                                        ' {MORE_BUTTON}',
                                    '</small>',
                                '</div>',
                                '<div class="clearfix"></div>',
                                '<div {MORE_ATTRS}>',
                                    '<p style="margin-top:10px;">',
                                        gettext('See the help to your right for information about setting examiners.'),
                                    '</p>',
                                    '<h4>',
                                        gettext('About examiners'),
                                    '</h4>',
                                    '<p>',
                                        devilry_subjectadmin.view.managestudents.ExaminersHelp.getIntroText(),
                                    '</p>',
                                    devilry_subjectadmin.view.managestudents.ExaminersHelp.getDetailsUl(),
                                '</div>',
                            '<tpl else>',
                                '<small>',
                                    gettext('This assignment will be published {pubtimeOffset}. Examiners and students can not see the assignment before it is published.'),
                                '</small>',
                            '</tpl>',
                        '</div>',
                    '</tpl>'
                ],
                messagedata: {
                    loading: true
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: '.make_me_examiner',
                    click: function(e) {
                        e.preventDefault();
                        this.fireEvent('make_me_examiner');
                    }
                }
            }, {
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
                    columnWidth: 0.40
                }]
            //}, {
                //xtype: 'box',
                //cls: 'bootstrap',
                //itemId: 'header',
                //margin: '20 0 0 0',
                //tpl: '<h3 class="muted">{heading}</h3>',
                //data: {
                    //heading: gettext('Deadlines, deliveries and feedback')
                //}
            }, {
                margin: '20 0 0 0',
                xtype: 'admingroupinfo_deadlinescontainer'
            }, {
                xtype: 'dangerousactions',
                margin: '20 0 0 0',
                titleTpl: '<h3>{heading}</h3>',
                items: [{
                    xtype: 'singleactionbox',
                    itemId: 'deleteButton',
                    margin: 0,
                    id: 'single_group_delete_button',
                    titleText: gettext('Delete'),
                    bodyHtml: gettext('Once you delete a group, there is no going back. Only superusers can delete a group with deliveries.'),
                    buttonText: gettext('Delete') + ' ...',
                    buttonUi: 'danger'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
