/**
 * Subject overview (overview of an subject).
 */
Ext.define('devilry_subjectadmin.view.subject.SubjectOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.subjectoverview',
    cls: 'devilry_subjectoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_extjsextras.SingleActionBox',
        'devilry_subjectadmin.view.EditSidebarContainer'
    ],


    /**
     * @cfg {String} subject_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            padding: '20 20 20 20',
            autoScroll: true,
            layout: 'column',

            items: [{
                xtype: 'editsidebarcontainer',
                layout: 'anchor',
                width: 250,
                margin: '0 0 0 0',
                padding: '0 10 0 10',
                items: [{
                    xtype: 'adminsbox',
                    anchor: '100%',
                    margin: '0 0 0 0'
                }]
            }, {
                xtype: 'container',
                columnWidth: 1.0,
                cls: 'devilry_focuscontainer',
                padding: '20',
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    margin: '0 0 20 0',
                    itemId: 'header',
                    tpl: '<h1 style="margin-top: 0;">{heading}</h1>',
                    data: {
                        heading: gettext('Loading') + ' ...'
                    }
                }, {
                    xtype: 'box',
                    cls: 'bootstrap devilry_subjectadmin_navigation',
                    tpl: [
                        '<p><strong><a href="{url}">{text}</a></strong></p>'
                    ],
                    data: {
                        url: devilry_subjectadmin.utils.UrlLookup.createNewPeriod(this.subject_id),
                        text: interpolate(gettext('Create new timeperiod'),
                    }
                }, {
                    xtype: 'listofperiods'
                }, {
                    xtype: 'dangerousactions',
                    margin: '45 0 0 0',
                    items: [{
                        xtype: 'singleactionbox',
                        margin: '0 0 0 0',
                        itemId: 'renameButton',
                        id: 'subjectRenameButton',
                        titleText: gettext('Loading') + ' ...',
                        bodyHtml: gettext('Renaming a course should not done without a certain amount of consideration. The name of a course, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                        buttonText: gettext('Rename') + ' ...'
                    }, {
                        xtype: 'singleactionbox',
                        itemId: 'deleteButton',
                        hidden: true,
                        id: 'subjectDeleteButton',
                        titleText: gettext('Loading') + ' ...',
                        bodyHtml: gettext('Once you delete a course, there is no going back. Only superusers can delete a non-empty course.'),
                        buttonText: gettext('Delete') + ' ...',
                        buttonUi: 'danger'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
