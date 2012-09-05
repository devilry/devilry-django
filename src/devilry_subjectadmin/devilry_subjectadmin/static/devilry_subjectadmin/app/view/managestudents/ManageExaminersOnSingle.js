Ext.define('devilry_subjectadmin.view.managestudents.ManageExaminersOnSingle', {
    extend: 'Ext.container.Container',
    alias: 'widget.manageexaminersonsingle',
    cls: 'devilry_subjectadmin_manageexaminersonsingle',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ExaminersInGroupGrid',
        'devilry_subjectadmin.view.managestudents.SelectExaminersGrid'
    ],

    /**
     * @cfg {Ext.data.Store} examinersStore (required)
     */

    more_text: gettext('Examiners provide feedback to a group. They can also add new deadlines for their groups, and open/close their groups.'),

    _createMoreInfo: function() {
        return this.more_text;
    },


    initComponent: function() {
        this.relatednote = interpolate(gettext('<strong>Note</strong>: Only %(examiners_term)s registered on the %(period_term)s are available.'), {
            examiners_term: gettext('examiners'),
            period_term: gettext('period')
        }, true);
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'box',
                anchor: '100%',
                tpl: [
                    '<h4>',
                        '{heading}',
                    '</h4>'
                ],
                data: {
                    heading: gettext('Examiners'),
                }
            }, {
                xtype: 'container',
                itemId: 'cardBody',
                layout: 'card',
                anchor: '100%',
                items: [{
                    xtype: 'panel',
                    itemId: 'helpAndButtonsContainer',
                    id: 'single_examiners_help_and_buttons_container',
                    border: false,
                    frame: false,
                    layout: 'anchor',
                    items: [{
                        xtype: 'examinersingroupgrid',
                        anchor: '100%',
                        store: this.examinersStore
                    }, {
                        xtype: 'moreinfobox',
                        anchor: '100%',
                        moretext: gettext('Examiners help ...'),
                        lesstext: gettext('Hide help'),
                        introtext: '',
                        small_morelink: true,
                        moreWidget: {
                            xtype: 'box',
                            html: this._createMoreInfo()
                        }
                    }],
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
                            text: gettext('Edit examiner(s)'),
                            itemId: 'setExaminerButton',
                            id: 'single_set_examiners_button',
                            tooltip: gettext('Edit examiner(s) to this group.')
                        }]
                    }],
                }, {
                    xtype: 'okcancelpanel',
                    itemId: 'setExaminersPanel',
                    border: 1,
                    bodyPadding: 10,
                    frame: false,
                    id: 'single_set_examiners_panel',
                    oktext: gettext('Save'),
                    layout: 'anchor',
                    items: [{
                        xtype: 'box',
                        anchor: '100%',
                        padding: '0 20 0 0',
                        tpl: [
                            '<p>{text}</p>',
                            '<p><small>{relatednote}</small></p>'
                        ],
                        data: {
                            text: interpolate(gettext('The selected %(examiners_term)s will <strong>replace</strong> any %(examiners_term)s currently on the %(group_term)s when you confirm your selection. Removing an %(examiner_term)s from the group does not affect any feedback they have already made on the group.'), {
                                examiner_term: gettext('examiner'),
                                examiners_term: gettext('examiners'),
                                group_term: gettext('group')
                            }, true),
                            relatednote: this.relatednote
                        }
                    }, {
                        xtype: 'selectexaminersgrid',
                        anchor: '100%'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
