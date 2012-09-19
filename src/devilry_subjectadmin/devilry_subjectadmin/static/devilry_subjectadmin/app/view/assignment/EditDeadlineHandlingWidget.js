/**
 * A widget that shows if an assignment is deadline_handling, and provides an edit
 * button which a controller can use to handle changing the attribute.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditDeadlineHandlingWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editdeadline_handling-widget',
    cls: 'devilry_subjectadmin_editdeadline_handling_widget',

    requires: [
        'devilry_subjectadmin.view.assignment.EditDeadlineHandlingPanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            deferredRender: true,
            items: [{
                xtype: 'editablesidebarbox',
                itemId: 'readDeadlineHandling',
                disabled: true,
                bodyTpl: [
                    '<tpl if="text">',
                        '<p class="muted">{text}</small>',
                    '<tpl else>',
                        '<tpl if="deadline_handling == SOFT">',
                            '<p><small class="muted">',
                                gettext('The assignment is configured to use SOFT deadlines. This means that students will be able to make deliveries after the deadline has expired. All deliveries after their deadline are clearly highligted.'),
                            '</p>',
                        '<tpl elseif="deadline_handling == HARD">',
                            '<p><small class="muted">',
                                gettext('The assignment is configured to use HARD deadlines. This means that students will be unable to make deliveries when a deadline has expired.'),
                            '</p>',
                        '<tpl else>',
                            // NOTE: We do not translate this, because it is a bug, and we do not raise an error because it is a bug that should not crash the entire UI.
                            '<p class="text-warning">This UI does not know how to handle <code>deadline_handling</code> values other that 0 and 1.</p>',
                        '</tpl>',
                    '</tpl>'
                ]
            }, {
                xtype: 'editdeadline_handlingpanel',
                itemId: 'editDeadlineHandling'
            }]
        });
        this.callParent(arguments);
    }
});
