/**
 * Subject overview (overview of an subject).
 */
Ext.define('devilry_subjectadmin.view.subject.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.subjectoverview',
    cls: 'devilry_subjectoverview',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.AdminsBox',
        'devilry_extjsextras.SingleActionBox'
    ],


    /**
     * @cfg {String} subject_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            frame: false,
            border: 0,
            bodyPadding: '20 40 20 40',
            autoScroll: true,

            items: [{
                xtype: 'alertmessagelist'
            }, {
                xtype: 'panel',
                frame: false,
                border: false,
                layout: 'column',
                items: [{
                    xtype: 'container',
                    columnWidth: 1,
                    layout: 'anchor',
                    defaults: {
                        anchor: '100%'
                    },
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
                        xtype: 'box',
                        cls: 'bootstrap devilry_subjectadmin_navigation',
                        tpl: [
                            '<p><strong><a href="{url}">{text}</a></strong></p>'
                        ],
                        data: {
                            url: devilry_subjectadmin.utils.UrlLookup.createNewPeriod(this.subject_id),
                            text: interpolate(gettext('Create new %(period_term)s'), {
                                period_term: gettext('period')
                            }, true)
                        }
                    }, {
                        xtype: 'listofperiods'
                    }, {
                        xtype: 'dangerousactions',
                        margin: '20 0 0 0',
                        items: [{
                            xtype: 'singleactionbox',
                            margin: '0 0 0 0',
                            itemId: 'renameButton',
                            id: 'subjectRenameButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Renaming a subject should not done without a certain amount of consideration. The name of a subject, especially the short name, is often used as an identifier when integrating other systems with Devilry.'),
                            buttonText: gettext('Rename') + ' ...'
                        }, {
                            xtype: 'singleactionbox',
                            itemId: 'deleteButton',
                            id: 'subjectDeleteButton',
                            titleText: gettext('Loading ...'),
                            bodyHtml: gettext('Once you delete a subject, there is no going back. Only superusers can delete a non-empty subject.'),
                            buttonText: gettext('Delete') + ' ...',
                            buttonUi: 'danger'
                        }]
                    }]
                }, {
                    xtype: 'container',
                    layout: 'anchor',
                    border: false,
                    width: 250,
                    margin: '6 0 0 40',
                    defaults: {
                        margin: '20 0 0 0'
                    },
                    items: [{
                        xtype: 'adminsbox',
                        anchor: '100%',
                        margin: '0 0 0 0'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
