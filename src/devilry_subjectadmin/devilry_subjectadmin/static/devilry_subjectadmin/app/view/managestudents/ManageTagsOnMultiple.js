Ext.define('devilry_subjectadmin.view.managestudents.ManageTagsOnMultiple', {
    extend: 'Ext.container.Container',
    alias: 'widget.managetagsonmultiple',
    cls: 'devilry_subjectadmin_managetagsonmultiple',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.TagsHelp'
    ],


    initComponent: function() {
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'box',
                anchor: '100%',
                tpl: [
                    '<h3>',
                        '{heading}',
                    '</h3>'
                ],
                data: {
                    heading: gettext('Tags')
                }
            }, {
                xtype: 'container',
                itemId: 'manageTagsCardBody',
                layout: 'card',
                anchor: '100%',
                items: [{
                    xtype: 'panel',
                    itemId: 'tagsHelpAndButtonsContainer',
                    id: 'multi_tags_help_and_buttons_container',
                    border: false,
                    frame: false,
                    layout: 'fit',
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        ui: 'footer',
                        padding: 0,
                        defaults: {
                            xtype: 'button',
                            scale: 'medium',
                            minWidth: 100
                        },
                        items: [{
                            text: gettext('Set tag(s)'),
                            itemId: 'setTagsButton',
                            id: 'multi_set_tags_button',
                            tooltip: gettext('Replace the tags on the selected groups with one or more new tag(s).')
                        }, {
                            text: gettext('Add tag(s)'),
                            itemId: 'addTagsButton',
                            id: 'multi_add_tags_button',
                            tooltip: gettext('Add one or more tag(s) to the selected groups.')
                        }, {
                            text: gettext('Clear tags'),
                            itemId: 'clearTagsButton',
                            ui: 'danger',
                            id: 'multi_clear_tags_button',
                            tooltip: gettext('Remove/clear all tags from the selected groups.')
                        }]
                    }],
                    items: {
                        xtype: 'moreinfobox',
                        introtext: devilry_subjectadmin.view.managestudents.TagsHelp.getIntroText(),
                        moreWidget: {
                            xtype: 'box',
                            html: [
                                devilry_subjectadmin.view.managestudents.TagsHelp.getDetailsUl(),
                                '<p><small class="muted">', devilry_subjectadmin.view.managestudents.TagsHelp.getPeriodNote(), '</small></p>'
                            ].join('')
                        }
                    }
                }, {
                    xtype: 'choosetagspanel',
                    itemId: 'setTagsPanel',
                    id: 'multi_set_tags_panel',
                    initialValue: '',
                    buttonText: gettext('Set tags')
                }, {
                    xtype: 'choosetagspanel',
                    itemId: 'addTagsPanel',
                    id: 'multi_add_tags_panel',
                    initialValue: '',
                    buttonText: gettext('Add tags')
                }, {
                    xtype: 'okcancelpanel',
                    itemId: 'clearTagsPanel',
                    id: 'multi_clear_tags_panel',
                    oktext: gettext('Clear tags'),
                    okbutton_ui: 'danger',
                    bodyPadding: 10,
                    html: [
                        '<p>',
                            gettext('Do you really want to clear all tags on the selected groups?'),
                        '</p>'
                    ].join('')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
