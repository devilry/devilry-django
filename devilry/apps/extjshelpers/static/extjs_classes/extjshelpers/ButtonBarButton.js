/** A button in a {@link devilry.extjshelpers.ButtonBar}. */
Ext.define('devilry.extjshelpers.ButtonBarButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.buttonbarbutton',
    scale: 'large',

    config: {
        /**
         * @cfg
         * ``Ext.XTemplate`` for tooltip. (Optional).
         */
        tooltipTpl: Ext.create('Ext.XTemplate',
            '<div class="tooltip-title">{title}</div><p>{body}</p>'
        ),

        /**
         * @cfg
         * Tooltip config. Should be an Object with title and body attributes. (Required).
         */
        tooltipCfg: undefined,

        /**
         * @cfg
         * If defined, the handler is set to open this url.
         */
        clickurl: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },
    
    initComponent: function() {
        var me = this;
        if(this.clickurl) {
            this.handler = function() {
                window.location = me.clickurl;
            }
        }
        Ext.apply(this, {
            listeners: {
                render: function() {
                    Ext.create('Ext.tip.ToolTip', {
                        target: me.id,
                        anchor: 'top',
                        dismissDelay: 30000,
                        html: me.tooltipTpl.apply(me.tooltipCfg)
                    });
                }
            },
        });
        this.callParent(arguments);
    }

});
