Ext.define('devilry_subjectadmin.view.gradeeditor.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.gradeeditoroverview',
    cls: 'devilry_subjectadmin_gradeeditoroverview',

    requires: [
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.gradeeditor.Edit',
        'devilry_subjectadmin.view.gradeeditor.Change'
    ],

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment to load deadlines for.
     */

    /**
     * @cfg {bool} [changeGradeEditor]
     * Show the grade editor changer on load?
     */

    frame: false,
    border: 0,
    bodyPadding: 40,
    autoScroll: true, // Autoscroll on overflow


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'alertmessagelist',
                itemId: 'globalAlertmessagelist'
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                html: [
                    '<h1>', gettext('Grade editor'), '</h1>',
                    '<p><small class="muted">',
                        gettext('To make it easy for examiners to create all the information related to a grade, Devilry use grade editors. Grade editors give examiners a unified user-interface tailored for different kinds of grading systems.'),
                    '</small></p>'
                ].join('')
            }, {
                xtype: 'gradeeditoredit'
            }, {
                xtype: 'gradeeditorchange',
                hidden: true
            }]
        });
        this.callParent(arguments);
    }
});
