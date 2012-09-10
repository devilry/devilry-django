/**
 * Related examiners overview.
 */
Ext.define('devilry_subjectadmin.view.relatedexaminers.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.relatedexaminers',
    cls: 'devilry_subjectadmin_relatedusers devilry_subjectadmin_relatedexaminers',
    requires: [
        'Ext.layout.container.Column',
        'devilry_subjectadmin.view.relatedexaminers.Grid',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_subjectadmin.view.relatedstudents.SelectUserPanel'
    ],

    frame: false,
    border: false,
    bodyPadding: 20,


    /**
     * @cfg {String} period_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'box',
                    columnWidth: 1,
                    cls: 'bootstrap',
                    anchor: '100%',
                    html: [
                        '<h1 style="margin-top: 0; padding-top: 0;">',
                            interpolate(gettext('Manage related %(examiners_term)s'), {
                                examiners_term: gettext('examiners')
                            }, true),
                        '</h1>',
                        '<p><small class="muted">',
                            interpolate(gettext('Manage the %(examiners_term)s available on this %(period_term)s.'), {
                                examiners_term: gettext('examiners'),
                                period_term: gettext('period')
                            }, true),
                        '</small></p>'
                    ].join('')
                }, {
                    width: 200,
                    xtype: 'primarybutton',
                    itemId: 'addButton',
                    margin: '15 0 0 0',
                    tabIndex: 1,
                    cls: 'add_related_user_button add_related_examiner_button',
                    text: gettext('Add examiner')
                }]
            }, {
                xtype: 'panel',
                border: false,
                layout: 'border',
                anchor: '100% -80',
                items: [{
                    xtype: 'relatedexaminersgrid',
                    region: 'center',
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        ui: 'footer',
                        items: [{
                            xtype: 'button',
                            ui: 'danger',
                            scale: 'large',
                            itemId: 'removeButton',
                            cls: 'remove_related_user_button remove_related_examiner_button',
                            disabled: true,
                            text: gettext('Remove selected')
                        }, '->', {
                            xtype: 'button',
                            scale: 'large',
                            itemId: 'tagsButton',
                            disabled: true,
                            cls: 'related_users_tags_button related_examiners_tags_button',
                            text: gettext('Tags'),
                            menu: [{
                                text: gettext('Clear tags'),
                                cls: 'clear_tags_button',
                                itemId: 'clearTagsButton'
                            }, {
                                text: gettext('Set tag(s)'),
                                cls: 'set_tags_button',
                                itemId: 'setTagsButton'
                            }, {
                                text: gettext('Add tag(s)'),
                                cls: 'add_tags_button',
                                itemId: 'addTagsButton'
                            }]
                        }]
                    }]
                }, {
                    xtype: 'container',
                    layout: 'anchor',
                    width: 400,
                    region: 'east',
                    padding: '0 0 0 30',
                    items: [{
                        xtype: 'panel',
                        border: false,
                        layout: 'card',
                        itemId: 'sidebarDeck',
                        items: [{
                            xtype: 'box',
                            itemId: 'helpBox',
                            cls: 'related_user_helpbox related_examiner_helpbox',
                            html: 'Help - TODO'
                        }, {
                            xtype: 'selectrelateduserpanel',
                            itemId: 'selectRelatedUserPanel'
                        }, {
                            xtype: 'okcancelpanel',
                            itemId: 'confirmRemovePanel',
                            cls: 'removeconfirmpanel bootstrap',
                            oktext: gettext('Remove selected'),
                            okbutton_ui: 'danger',
                            bodyPadding: 10,
                            html: [
                                '<p>',
                                    gettext('Do you really want to remove all the selected related examiners?'),
                                    interpolate(gettext('They will not be removed from any existing assignments. You will not be able to add them on any new assignments, and they will not be available in statistics for the entire %(period_term)s.'), {
                                        period_term: gettext('period')
                                    }, true),
                                '</p>'
                            ].join('')
                        }, {
                            xtype: 'choosetagspanel',
                            itemId: 'setTagsPanel',
                            cls: 'set_tags_panel',
                            buttonText: gettext('Set tags')
                        }, {
                            xtype: 'choosetagspanel',
                            itemId: 'addTagsPanel',
                            cls: 'add_tags_panel',
                            buttonText: gettext('Add tags')
                        }, {
                            xtype: 'okcancelpanel',
                            itemId: 'clearTagsPanel',
                            cls: 'clear_tags_panel',
                            oktext: gettext('Clear tags'),
                            okbutton_ui: 'danger',
                            bodyPadding: 10,
                            html: [
                                '<p>',
                                    gettext('Do you really want to clear all tags on the selected examiners?'),
                                '</p>'
                            ].join('')
                        }]
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
