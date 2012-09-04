Ext.define('devilry_subjectadmin.view.managestudents.ManageExaminersOnMultiple', {
    extend: 'Ext.container.Container',
    alias: 'widget.manageexaminersonmultiple',
    cls: 'devilry_subjectadmin_manageexaminersonmultiple',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        //'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_extjsextras.OkCancelPanel',
    ],

    intro_text: interpolate(gettext('TODO'), {
    }, true),

    details_points: [
        'TODO'
    ],

    _createMoreInfo: function() {
        return Ext.create('Ext.XTemplate', 
            '<ul>',
                '<tpl for="points">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>'
        ).apply({
            points: this.details_points
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
                    heading: gettext('Manage examiners'),
                }
            }, {
                xtype: 'container',
                itemId: 'cardBody',
                layout: 'card',
                anchor: '100%',
                items: [{
                    xtype: 'panel',
                    itemId: 'helpAndButtonsContainer',
                    id: 'multi_examiners_help_and_buttons_container',
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
                            text: gettext('Set examiner(s)'),
                            itemId: 'setExaminersButton',
                            id: 'multi_set_examiners_button',
                            tooltip: gettext('Replace the examiners on the selected groups with one or more new examiner(s).')
                        }, {
                            text: gettext('Add examiner(s)'),
                            itemId: 'addExaminersButton',
                            id: 'multi_add_examiners_button',
                            tooltip: gettext('Add one or more examiner(s) to the selected groups.')
                        }, {
                            text: gettext('Clear examiners'),
                            itemId: 'clearExaminersButton',
                            ui: 'danger',
                            id: 'multi_clear_examiners_button',
                            tooltip: gettext('Remove/clear all examiners from the selected groups.')
                        }]
                    }],
                    items: {
                        xtype: 'moreinfobox',
                        margin: '10 0 0 0',
                        introtext: this.intro_text,
                        moreWidget: {
                            xtype: 'box',
                            html: this._createMoreInfo()
                        }
                    }
                }, {
                    xtype: 'box',
                    itemId: 'setExaminersPanel',
                    id: 'multi_set_examiners_panel',
                    html: gettext('Set examiners')
                }, {
                    xtype: 'box',
                    itemId: 'addExaminersPanel',
                    id: 'multi_add_examiners_panel',
                    html: gettext('Add examiners')
                }, {
                    xtype: 'okcancelpanel',
                    itemId: 'clearExaminersPanel',
                    id: 'multi_clear_examiners_panel',
                    oktext: gettext('Clear examiners'),
                    okbutton_ui: 'danger',
                    bodyPadding: 10,
                    html: [
                        '<p>',
                            gettext('Do you really want to clear all examiners on the selected groups?'),
                        '</p>'
                    ].join('')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
