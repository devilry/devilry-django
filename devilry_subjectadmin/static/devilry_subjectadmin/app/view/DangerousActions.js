Ext.define('devilry_subjectadmin.view.DangerousActions', {
    extend: 'devilry_extjsextras.UnfocusedContainer',
    alias: 'widget.dangerousactions',
    cls: 'devilry_subjectadmin_dangerousactions',

    title: gettext('Dangerous actions'),
    titleTpl: '<h2>{heading}</h2>',

    defaultOpacity: 0.5,
    hoverOpacity: 1,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                cls: 'bootstrap header',
                itemId: 'header',
                tpl: this.titleTpl,
                data: {
                    heading: this.title
                }
            }, {
                xtype: 'container',
                padding: '10 10 10 10',
                cls: 'body',
                layout: 'anchor',
                defaults: {
                    anchor: '100%',
                    margin: '10 0 0 0',
                    bodyTpl: '<p class="muted">{html}</p>'
                },
                items: this.items
            }]
        });
        this.callParent(arguments);
    }
});
