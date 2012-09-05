Ext.define('devilry_subjectadmin.view.managestudents.ManageTagsOnMultiple', {
    extend: 'Ext.container.Container',
    alias: 'widget.managetagsonmultiple',
    cls: 'devilry_subjectadmin_managetagsonmultiple',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_extjsextras.OkCancelPanel',
    ],

    tag_introtext: interpolate(gettext('%(Tags_term)s is a flexible method of organizing %(groups_term)s. Only administrators can see %(tags_term)s. You can search and select %(groups_term)s by their %(tags_term)s. Common use-cases are:'), {
        Tags_term: gettext('Tags'),
        groups_term: gettext('groups'),
        tags_term: gettext('tags')
    }, true),

    tag_details_points: [
        interpolate(gettext('Mark %(groups_term)s with special needs.'), {
            groups_term: gettext('groups')
        }, true),
        interpolate(gettext('Organize %(groups_term)s attending the same classroom sessions.'), {
            groups_term: gettext('groups')
        }, true),
        gettext('Mark suspected cheaters.')
    ],

    tag_details_periodnote: interpolate(gettext('<strong>NOTE:</strong> %(Tags_term)s on %(groups_term)s must not be confused with %(tags_term)s on %(students_term)s and %(examiners_term)s on a %(period_term)s. Those %(tags_term)s are used to automate assigning examiners to students. %(Tags_term)s from the %(period_term)s may have been included when you added %(groups_term)s to this %(assignment_term)s, however you can safely edit %(tags_term)s on %(groups_term)s without affecting the %(tags_term)s on the %(period_term)s.'), {
        Tags_term: gettext('Tags'),
        groups_term: gettext('groups'),
        tags_term: gettext('tags'),
        examiners_term: gettext('examiners'),
        students_term: gettext('students'),
        period_term: gettext('period'),
        assignment_term: gettext('assignment')
    }, true),

    _createTagMoreHelp: function() {
        return Ext.create('Ext.XTemplate', 
            '<ul>',
                '<tpl for="points">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>',
            '<p>',
                this.tag_details_periodnote,
            '</p>'
        ).apply({
            points: this.tag_details_points
        });
    },


    initComponent: function() {
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'box',
                anchor: '100%',
                tpl: [
                    '<h2>',
                        '{heading}',
                    '</h2>'
                ],
                data: {
                    heading: gettext('Manage tag(s)'),
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
                        introtext: this.tag_introtext,
                        moreWidget: {
                            xtype: 'box',
                            html: this._createTagMoreHelp()
                        }
                    }
                }, {
                    xtype: 'choosetagspanel',
                    itemId: 'setTagsPanel',
                    id: 'multi_set_tags_panel',
                    buttonText: gettext('Set tags')
                }, {
                    xtype: 'choosetagspanel',
                    itemId: 'addTagsPanel',
                    id: 'multi_add_tags_panel',
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
