/**
 * A widget that shows if an assignment is anonymous, and provides an edit
 * button which a controller can use to handle changing the attribute.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditAnonymousWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editanonymous-widget',
    cls: 'devilry_subjectadmin_editanonymous_widget',

    requires: [
        'devilry_extjsextras.ContainerWithEditTitle',
        'devilry_extjsextras.MarkupMoreInfoBox',
        'devilry_subjectadmin.view.assignment.EditAnonymousPanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            deferredRender: true,
            items: [{
                xtype: 'containerwithedittitle',
                itemId: 'readAnonymous',
                disabled: true,
                body: {
                    xtype: 'markupmoreinfobox',
                    moreCls: 'alert alert-info',
                    tpl: [
                        '<tpl if="loading">',
                            '<p class="muted">{loading}</p>',
                        '<tpl else>',
                            '<p class="muted"><small>',
                                '{info}',
                            ' {MORE_BUTTON}</small></p>',
                            '<p {MORE_ATTRS}>',
                                gettext('For exams, assignments should normally be anonymous.'),
                                ' ',
                                gettext('If an assignment is anonymous, examiners see candidate-id instead of any personal information about the students.'),
                            '</p>',
                        '</tpl>'
                    ],
                    data: {
                        loading: gettext('Loading') + ' ...'
                    }
                }
            }, {
                xtype: 'editanonymouspanel',
                itemId: 'editAnonymous'
            }]
        });
        this.callParent(arguments);
    }
});
