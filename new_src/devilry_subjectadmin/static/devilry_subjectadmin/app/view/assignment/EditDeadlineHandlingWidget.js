/**
 * A widget that shows if an assignment is deadline_handling, and provides an edit
 * button which a controller can use to handle changing the attribute.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditDeadlineHandlingWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editdeadline_handling-widget',
    cls: 'devilry_subjectadmin_editdeadline_handling_widget',

    requires: [
        'devilry_extjsextras.ContainerWithEditTitle',
        'devilry_extjsextras.MarkupMoreInfoBox',
        'devilry_subjectadmin.view.assignment.EditDeadlineHandlingPanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            deferredRender: true,
            items: [{
                xtype: 'containerwithedittitle',
                itemId: 'readDeadlineHandling',
                disabled: true,
                title: gettext('Deadline handling'),
                body: {
                    xtype: 'markupmoreinfobox',
                    moreCls: 'alert alert-info',
                    tpl: [
                        '<tpl if="text">',
                            '<p class="muted">{text}</small>',
                        '<tpl else>',
                            '<p class="muted">',
                                '<tpl if="deadline_handling == SOFT">',
                                    gettext('Soft deadlines'),
                                '<tpl elseif="deadline_handling == HARD">',
                                    gettext('Hard deadlines'),
                                '<tpl else>',
                                    // NOTE: We do not translate this, because it is a bug, and we do not raise an error because it is a bug that should not crash the entire UI.
                                    '<span class="text-warning">This UI does not know how to handle <code>deadline_handling</code> values other that 0 and 1.</p>',
                                '</tpl>',
                                ' <small>{MORE_BUTTON}</small>',
                            '</p>',
                            '<div {MORE_ATTRS}>',

                                '<p>',
                                    gettext('With HARD deadlines, students will be unable to make deliveries when a deadline has expired.'),
                                '</p>',
                                '<p>',
                                    gettext('With SOFT deadlines students will be able to make deliveries after the deadline has expired. All deliveries after their deadline are clearly highligted.'),
                                '</p>',
                                '<p><small>',
                                    gettext('NOTE: Devilry is designed from the bottom up to gracefully handle SOFT deadlines. Students have to perform an extra confirm-step when adding deliveries after their active deadline, and assignments where the deadline has expired is clearly marked for both students and examiners.'),
                                '</small></p>',
                            '</div>',
                        '</tpl>'
                    ],
                    data: {
                        text: gettext('Loading') + ' ...'
                    }
                }
            }, {
                xtype: 'editdeadline_handlingpanel',
                itemId: 'editDeadlineHandling'
            }]
        });
        this.callParent(arguments);
    }
});
