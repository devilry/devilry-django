Ext.define('devilry_subjectadmin.view.period.EditDurationWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.editperiod_duration-widget',
    cls: 'devilry_subjectadmin_editperiod_duration_widget',

    requires: [
        'devilry_extjsextras.ContainerWithEditTitle',
        'devilry_extjsextras.MarkupMoreInfoBox',
        'devilry_subjectadmin.view.period.EditDurationPanel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'card',
            deferredRender: true,
            items: [{
                xtype: 'containerwithedittitle',
                itemId: 'readDuration',
                disabled: true,
                title: gettext('Duration'),
                body: {
                    xtype: 'markupmoreinfobox',
                    //moreCls: 'alert alert-info',
                    tpl: [
                        '<tpl if="text">',
                            '<p class="muted">{text}</p>',
                        '<tpl else>',
                            '<p class="muted">',
                                '<small class="muted durationdisplay">{start_time} &mdash; {end_time}</small>',
                                //'<br/>',
                                //'<small>{MORE_BUTTON}</small>',
                            '</p>',
                            //'<p {MORE_ATTRS}>',
                            //'</p>',
                        '</tpl>'
                    ]
                }
            }, {
                xtype: 'editperiod_duration',
                itemId: 'editDuration'
            }]
        });
        this.callParent(arguments);
    }
});
