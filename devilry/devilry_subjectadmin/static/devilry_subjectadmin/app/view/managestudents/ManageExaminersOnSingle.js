Ext.define('devilry_subjectadmin.view.managestudents.ManageExaminersOnSingle', {
    extend: 'Ext.container.Container',
    alias: 'widget.manageexaminersonsingle',
    cls: 'devilry_subjectadmin_manageexaminersonsingle',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ExaminersInGroupGrid',
        'devilry_subjectadmin.view.managestudents.ExaminersHelp',
        'devilry_extjsextras.ContainerWithEditTitle',
        'devilry_subjectadmin.view.managestudents.SelectExaminersGrid'
    ],

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
        ];
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
        this.relatednote = gettext('<strong>Note</strong>: Only examiners registered on the current timeperiod are available.'),
        Ext.apply(this, {
            cls: 'bootstrap',
            layout: 'anchor',
            items: [{
                xtype: 'containerwithedittitle',
                anchor: '100%',
                title: gettext('Examiners'),
                listeners: {
                    scope: this,
                    edit: function() {
                        this.fireEvent('edit_examiners', this);
                    }
                }
            }, {
                xtype: 'container',
                itemId: 'cardBody',
                layout: 'card',
                deferredRender: true,
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
                        anchor: '100%'
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
                        itemId: 'helpBox',
                        tpl: [
                            '<p>',
                                gettext('The selected examiners will <strong>replace</strong> any examiners currently on the group when you confirm your selection. Removing an examiner from the group does not affect any feedback they have already made on the group.'),
                            '</p>',
                            '{relatednote}'
                        ],
                        data: {
                            relatednote: gettext('Loading') + ' ...'
                        }
                    }, {
                        xtype: 'selectexaminersgrid',
                        anchor: '100%'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    setPeriodId: function(period_id) {
        this.down('#helpBox').update({
            relatednote: devilry_subjectadmin.view.managestudents.ExaminersHelp.getRelatedNote(period_id)
        });
    }
});
