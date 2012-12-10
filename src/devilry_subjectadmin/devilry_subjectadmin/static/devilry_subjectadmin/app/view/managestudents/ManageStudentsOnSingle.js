Ext.define('devilry_subjectadmin.view.managestudents.ManageStudentsOnSingle', {
    extend: 'Ext.container.Container',
    alias: 'widget.managestudentsonsingle',
    cls: 'devilry_subjectadmin_managestudentsonsingle',
    requires: [
        'devilry_extjsextras.MoreInfoBox',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.StudentsInGroupGrid'
    ],

    more_text: [
        '<p>',
            gettext('A group can have one or more students.'), ' ',
            gettext('Feedback is given to a group as a whole, not to individual students on a group.'),
        '</p>'
    ].join(''),

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
                    heading: gettext('Students')
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
                    id: 'single_students_help_and_buttons_container',
                    border: false,
                    frame: false,
                    layout: 'anchor',
                    items: [{
                        xtype: 'studentsingroupgrid',
                        anchor: '100%'
                    }, {
                        xtype: 'moreinfobox',
                        anchor: '100%',
                        moretext: gettext('Students help ...'),
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
                    itemId: 'confirmPop',
                    id: 'single_students_confirm_pop',
                    okbutton_ui: 'danger',
                    bodyPadding: 10,
                    html: [
                        '<p>',
                            gettext('Do you really want to split this group in two? This will move the selected student from this project group, into a copy of this group. Copies everything except the other students (deadlines, deliveries, feedback, tags and examiners).'),
                        '</p>'
                    ].join('')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
