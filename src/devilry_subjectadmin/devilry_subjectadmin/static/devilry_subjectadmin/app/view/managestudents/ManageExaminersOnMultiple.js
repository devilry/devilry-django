Ext.define('devilry_subjectadmin.view.managestudents.ManageExaminersOnMultiple', {
    extend: 'Ext.container.Container',
    alias: 'widget.manageexaminersonmultiple',
    cls: 'devilry_subjectadmin_manageexaminersonmultiple',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_subjectadmin.view.managestudents.SelectExaminersGrid',
        'devilry_subjectadmin.view.managestudents.ExaminersHelp',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.OkCancelPanel'
    ],

    /**
     * @cfg {int} [period_id]
     * The ID of the current period.
     */

    _createMoreInfo: function() {
        return devilry_subjectadmin.view.managestudents.ExaminersHelp.getDetailsUl();
    },


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
                    heading: gettext('Examiners')
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
                            text: gettext('Advanced'),
                            id: 'multi_advanced_examiners_button',
                            menu: [{
                                text: gettext('Random distribute'),
                                itemId: 'randomDistributeExaminersButton',
                                id: 'multi_randomdistribute_examiners_button',
                                tooltip: gettext('Replace the examiners on the selected groups with a random examiner from a set of examiners that you select. The distribution of groups for each examiner is even, no examiners get more that one group more than any other examiner.')
                            }]
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
                        introtext: devilry_subjectadmin.view.managestudents.ExaminersHelp.getIntroText(),
                        moreWidget: {
                            xtype: 'box',
                            html: this._createMoreInfo()
                        }
                    }
                }, {
                    xtype: 'okcancelpanel',
                    border: 1,
                    bodyPadding: 10,
                    frame: false,
                    itemId: 'setExaminersPanel',
                    id: 'multi_set_examiners_panel',
                    oktext: gettext('Set selected examiners'),
                    layout: 'column',
                    items: [{
                        xtype: 'box',
                        anchor: '100%',
                        columnWidth: 0.5,
                        padding: '0 20 0 0',
                        itemId: 'helpBox',
                        tpl: [
                            '<p>',
                                gettext('Select one or more examiner. Any current examiners on the selected groups will be <strong>replaced</strong> when you confirm your selection.'),
                            '</p>',
                            '{relatednote}'
                        ],
                        data: {
                            relatednote: ''
                        }
                    }, {
                        xtype: 'selectexaminersgrid',
                        columnWidth: 0.5,
                        anchor: '100%'
                    }]
                }, {
                    xtype: 'okcancelpanel',
                    border: 1,
                    bodyPadding: 10,
                    frame: false,
                    itemId: 'randomDistributeExaminersPanel',
                    id: 'multi_randomdistribute_examiners_panel',
                    oktext: gettext('Random distribute selected examiners'),
                    layout: 'column',
                    items: [{
                        xtype: 'box',
                        anchor: '100%',
                        columnWidth: 0.5,
                        padding: '0 20 0 0',
                        itemId: 'helpBox',
                        tpl: [
                            '<p>',
                                gettext('Select one or more examiner. Any current examiners on the selected groups will be <strong>replaced</strong> when you confirm your selection.'),
                            '</p>',
                            '{relatednote}'
                        ],
                        data: {
                            relatednote: ''
                        }
                    }, {
                        xtype: 'selectexaminersgrid',
                        columnWidth: 0.5,
                        anchor: '100%'
                    }]
                }, {
                    xtype: 'okcancelpanel',
                    border: 1,
                    bodyPadding: 10,
                    frame: false,
                    itemId: 'addExaminersPanel',
                    id: 'multi_add_examiners_panel',
                    oktext: gettext('Add selected examiners'),
                    layout: 'column',
                    items: [{
                        xtype: 'box',
                        anchor: '100%',
                        columnWidth: 0.5,
                        padding: '0 20 0 0',
                        itemId: 'helpBox',
                        tpl: [
                            '<p>',
                                gettext('Select one or more examiner. The selected examiners will be <strong>added</strong> to the selected groups when you confirm your selection.'),
                            '</p>',
                            '{relatednote}'
                        ],
                        data: {
                            relatednote: ''
                        }
                    }, {
                        xtype: 'selectexaminersgrid',
                        columnWidth: 0.5,
                        anchor: '100%'
                    }]
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
    },

    setPeriodId: function(period_id) {
        if(this.period_id === period_id) {
            return;
        }
        this.period_id = period_id;
        var helpBoxes = this.query('#helpBox');
        Ext.Array.each(helpBoxes, function(helpBox) {
            helpBox.update({
                relatednote: devilry_subjectadmin.view.managestudents.ExaminersHelp.getRelatedNote(period_id)
            });
        }, this);
    }
});
