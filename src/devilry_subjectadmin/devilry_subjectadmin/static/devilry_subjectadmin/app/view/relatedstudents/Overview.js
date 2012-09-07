/**
 * Related students overview.
 */
Ext.define('devilry_subjectadmin.view.relatedstudents.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.relatedstudents',
    cls: 'devilry_subjectadmin_relatedusers devilry_subjectadmin_relatedstudents',
    requires: [
        'Ext.layout.container.Column',
        'devilry_subjectadmin.view.relatedstudents.Grid',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.relatedstudents.SelectUserPanel'
    ],

    frame: false,
    border: false,
    bodyPadding: 40,


    /**
     * @cfg {String} period_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                anchor: '100%',
                html: [
                    '<h1>',
                        interpolate(gettext('Manage related %(students_term)s'), {
                            students_term: gettext('students')
                        }, true),
                    '</h1>',
                    '<p><small class="muted">',
                        interpolate(gettext('Manage the %(students_term)s available on this %(period_term)s.'), {
                            students_term: gettext('students'),
                            period_term: gettext('period')
                        }, true),
                    '</small></p>'
                ].join('')
            }, {
                xtype: 'panel',
                border: false,
                layout: 'border',
                anchor: '100% -80',
                items: [{
                    xtype: 'relatedstudentsgrid',
                    region: 'center',
                    fbar: [{
                        xtype: 'button',
                        ui: 'danger',
                        scale: 'large',
                        itemId: 'removeButton',
                        cls: 'remove_related_user_button remove_related_student_button',
                        disabled: true,
                        text: gettext('Remove selected')
                    }, {
                        xtype: 'primarybutton',
                        itemId: 'addButton',
                        cls: 'add_related_user_button add_related_student_button',
                        text: gettext('Add student')
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
                            cls: 'related_user_helpbox related_student_helpbox',
                            html: 'Help - TODO'
                        }, {
                            xtype: 'selectrelateduserpanel',
                            itemId: 'selectRelatedUserPanel'
                        }, {
                            xtype: 'okcancelpanel',
                            itemId: 'confirmRemovePanel',
                            cls: 'removeconfirmpanel',
                            oktext: gettext('Remove selected'),
                            okbutton_ui: 'danger',
                            bodyPadding: 10,
                            html: [
                                '<p>',
                                    gettext('Do you really want to remove all the selected related students?'),
                                    interpolate(gettext('They will not be removed from any existing assignments. You will not be able to add them on any new assignments, and they will not be available in statistics for the entire %(period_term)s.'), {
                                        period_term: gettext('period')
                                    }, true),
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
