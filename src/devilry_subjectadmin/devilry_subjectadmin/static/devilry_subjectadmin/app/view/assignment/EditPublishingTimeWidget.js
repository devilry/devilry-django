/**
 * A widget that shows if an assignment is published, when it was/is-to-be
 * published, and provides an edit button which a controller can use to
 * display widget to change the publishing_time.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditPublishingTimeWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editpublishingtime-widget',
    cls: 'devilry_subjectadmin_editpublishingtime_widget',

    requires: [
        'devilry_subjectadmin.view.assignment.EditPublishingTimePanel',
        'devilry_extjsextras.ContainerWithEditTitle'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            deferredRender: true,
            items: [{
                xtype: 'containerwithedittitle',
                itemId: 'readPublishingTime',
                disabled: true,
                body: {
                    xtype: 'markupmoreinfobox',
                    moreCls: 'alert alert-info',
                    tpl: [
                        '<p>',
                            '<tpl if="loading">',
                                '<small class="muted">{loading}</small>',
                            '<tpl else>',
                                '<tpl if="is_published">',
                                    '<span class="text-success">{offset_from_now}</span>',
                                '<tpl else>',
                                    '<span class="text-warning">{offset_from_now}</span>',
                                '</tpl>',
                                ' <small class="muted">({publishing_time})</small>',
                                '<br/><small>{MORE_BUTTON}</small>',
                            '</tpl>',
                        '</p>',
                        '<div {MORE_ATTRS}>',
                            gettext('The time when students will be able to start adding deliveries on the assignment.'),
                        '</div>'
                    ],
                    data: {
                        loading: gettext('Loading') + ' ...'
                    }
                }
            }, {
                xtype: 'editpublishingtimepanel',
                itemId: 'editPublishingTime'
            }]
        });
        this.callParent(arguments);
    }
});
