Ext.define('devilry_subjectadmin.view.managestudents.ManageExaminersOnSingle', {
    extend: 'Ext.container.Container',
    alias: 'widget.manageexaminersonsingle',
    cls: 'devilry_subjectadmin_manageexaminersonsingle',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ExaminersInGroupGrid',
        'devilry_subjectadmin.view.managestudents.ExaminersHelp',
        'devilry_subjectadmin.view.managestudents.SelectExaminersGrid'
    ],

    /**
     * @cfg {Ext.data.Store} examinersStore (required)
     */

    /**
     * @cfg {int} [period_id]
     * The ID of the current period.
     */

    _createMoreInfo: function() {
        return [
            '<p>',
                devilry_subjectadmin.view.managestudents.ExaminersHelp.getIntroText(),
            '</p>',
            devilry_subjectadmin.view.managestudents.ExaminersHelp.getDetailsUl()
        ]
    },

    constructor: function(config) {
        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            /**
             * @event
             * Fired when edit-examiners is clicked.
             * @param panel This panel.
             */
            'edit_examiners'
        );
        this.callParent([config]);
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
                        ' <a href="#" class="edit_examiners_button">(',
                            gettext('Edit'),
                        ')</a>',
                    '</h4>'
                ],
                data: {
                    heading: gettext('Examiners'),
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a.edit_examiners_button',
                    click: function(e) {
                        e.preventDefault();
                        this.fireEvent('edit_examiners', this);
                    }
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
                    }]
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
                        tpl: [
                            '<p>{text}</p>',
                            '{relatednote}'
                        ],
                        data: {
                            text: interpolate(gettext('The selected %(examiners_term)s will <strong>replace</strong> any %(examiners_term)s currently on the %(group_term)s when you confirm your selection. Removing an %(examiner_term)s from the group does not affect any feedback they have already made on the group.'), {
                                examiner_term: gettext('examiner'),
                                examiners_term: gettext('examiners'),
                                group_term: gettext('group')
                            }, true),
                            relatednote: devilry_subjectadmin.view.managestudents.ExaminersHelp.getRelatedNote(this.period_id)
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
