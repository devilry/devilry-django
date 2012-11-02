Ext.define('devilry_subjectadmin.view.DangerousActions', {
    extend: 'Ext.container.Container',
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
                cls: 'bootstrap',
                //margin: '0 0 2 0',
                itemId: 'header',
                tpl: this.titleTpl,
                data: {
                    heading: this.title
                }
            }, {
                xtype: 'panel',
                bodyPadding: 10,
                layout: 'anchor',
                defaults: {
                    anchor: '100%',
                    margin: '10 0 0 0',
                    bodyTpl: '<p class="muted">{html}</p>'
                },
                items: this.items
            }]
        });
        this.on('render', this._onRender, this);
        this.callParent(arguments);
    },

    _onRender: function() {
        this.getEl().setOpacity(this.defaultOpacity);
        this.getEl().on({
            scope: this,
            mouseenter: this._onMouseEnter,
            mouseleave: this._onMouseLeave
        });
    },

    _onMouseEnter: function() {
        this.getEl().setOpacity(this.hoverOpacity);
    },

    _onMouseLeave: function() {
        this.getEl().setOpacity(this.defaultOpacity);
    }
});
