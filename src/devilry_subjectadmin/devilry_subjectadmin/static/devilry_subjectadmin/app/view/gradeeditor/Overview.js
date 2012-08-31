Ext.define('devilry_subjectadmin.view.gradeeditor.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.gradeeditoroverview',
    cls: 'devilry_subjectadmin_gradeeditoroverview',

    requires: [
        'devilry_extjsextras.AlertMessageList'
    ],

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment to load deadlines for.
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
                    '<h1>', gettext('Edit grade editor'), '</h1>',
                    '<p><small>',
                        gettext('To make it easy for examiners to create all the information related to a grade, Devilry use grade editors. Grade editors give examiners a unified user-interface tailored for different kinds of grading systems.'),
                    '</small></p>'
                ].join('')
            }, {
                xtype: 'box',
                itemId: 'about',
                cls: 'bootstrap',
                tpl: [
                    '<tpl if="loading">',
                        '<h2>', gettext('Loading'), ' ...</h2>',
                    '<tpl else>',
                        '<h2>',
                            gettext('Current grade editor'),
                            ': {registryitem.title}',
                            ' <a href="#" class="change_gradeeditor_link">(',
                                gettext('Change'),
                            ')</a>',
                        '</h2>',
                        '<div>',
                            '{registryitem.description}',
                        '</div>',
                    '</tpl>'
                ],
                data: {
                    loading: true
                }
            }, {
                xtype: 'container',
                itemId: 'configContainer',
                layout: 'fit',
                items: []
            }]
        });
        this.callParent(arguments);
    }
});
