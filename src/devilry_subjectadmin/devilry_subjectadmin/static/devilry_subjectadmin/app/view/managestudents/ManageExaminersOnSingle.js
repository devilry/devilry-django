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
                            text: gettext('Add examiner(s)'),
                            itemId: 'addExaminerButton',
                            id: 'single_add_examiners_button',
                            tooltip: gettext('Add examiner(s) to this group.')
                        }]
                    }],
                }, {
                    xtype: 'okcancelpanel',
                    itemId: 'confirmRemove',
                    id: 'single_examiners_confirm_remove',
                    okbutton_ui: 'danger',
                    bodyPadding: 10,
                    html: [
                        '<p>',
                            gettext('Do you really want to remove this examiner from this group? Any feedback the examiner have already provided the group will we left untouched. The only change will be that the examiner looses access to the group.'),
                        '</p>'
                    ].join('')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
