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
                title: gettext('Anonymity'),
                body: {
                    xtype: 'markupmoreinfobox',
                    moreCls: 'alert alert-info',
                    tpl: [
                        '<tpl if="loading">',
                            '<p class="muted">{loading}</p>',
                        '<tpl else>',
                            '<p class="muted">',
                                '<tpl if="anonymous">',
                                    gettext('Anonymous'),
                                '<tpl else>',
                                    gettext('Not anonymous'),
                                '</tpl>',
                                ' <small> {MORE_BUTTON}</small>',
                            '</p>',
                            '<div {MORE_ATTRS}>',
                                '<p>',
                                    gettext('On anonymous assignments, examiners and students can NOT see each other and they can NOT communicate.'),
                                '</p>',
                                '<p>',
                                    gettext('If an assignment is anonymous, examiners see candidate-id instead of any personal information about the students.'),
                                '</p>',
                                '<p>',
                                    gettext('This means that anonymous assignments is perfect for exams, and for assignments where you do not want prior experiences with a student to affect results.'),
                                '</p>',
                            '</div>',
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
