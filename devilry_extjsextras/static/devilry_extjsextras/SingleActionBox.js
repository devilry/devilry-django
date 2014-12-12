/**
 * A box with text and a button.
 * */ 
Ext.define('devilry_extjsextras.SingleActionBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.singleactionbox',
    cls: 'devilry_singleactionbox bootstrap',

    /**
     * @cfg {String} [bodyTpl]
     * The body template.
     */
    bodyTpl: '<p>{html}</p>',

    /**
     * @cfg {Object} [bodyData=undefined]
     * Data for the ``bodyTpl``. Defaults to ``{html: bodyHtml}``.
     */

    /**
     * @cfg {string} [bodyHtml=undefined]
     */

    /**
     * @cfg {string} titleText (Required)
     */

    /**
     * @cfg {string} titleTpl (Optional)
     * Title template. Defaults to ``<strong>{text}</strong>``.
     */
    titleTpl: '<strong>{text}</strong>',

    /**
     * @cfg {string} buttonText (Required)
     */

    /**
     * @cfg {string} buttonScale (Optional)
     * Defaults to "medium".
     */
    buttonScale: 'medium',

    /**
     * @cfg {string} buttonWidth (Optional)
     * Defaults to ``130``.
     */
    buttonWidth: 130,

    /**
     * @cfg {Object} buttonListeners (Required)
     */

    /**
     * @cfg {String} [buttonUi="default"]
     * The ``ui``-attribute of the button.
     */
    buttonUi: 'default',

    initComponent: function() {
        this.addEvents({
            /**
             * @event
             * Fired when clicking the button.
             * @param {devilry_extjsextras.SingleActionBox} singleactionbox
             * */
            click: true
        });
        var bodyData = this.bodyData;
        if(Ext.isEmpty(bodyData)) {
            bodyData = {html: this.bodyHtml};
        }
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                anchor: '100%',
                xtype: 'box',
                itemId: 'singleactionbox_title',
                tpl: this.titleTpl,
                data: {
                    text: this.titleText
                }
            }, {
                anchor: '100%',
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'box',
                    itemId: 'singleactionbox_body',
                    tpl: this.bodyTpl,
                    data: bodyData,
                    padding: '0 20 0 0',
                    columnWidth: 1
                }, {
                    xtype: 'button',
                    scale: this.buttonScale,
                    text: this.buttonText,
                    ui: this.buttonUi,
                    itemId: 'singleactionbox_button',
                    width: this.buttonWidth,
                    listeners: {
                        scope: this,
                        click: this._onClick
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    setBodyHtml: function(html) {
        this.down('#singleactionbox_body').update({
            html: html
        });
    },
    setTitleText: function(text) {
        this.down('#singleactionbox_title').update({
            text: text
        });
    },
    setButtonText: function(text) {
        this.down('#singleactionbox_button').setText(text);
    },

    _onClick: function() {
        this.fireEvent('click', this);
    }
});
