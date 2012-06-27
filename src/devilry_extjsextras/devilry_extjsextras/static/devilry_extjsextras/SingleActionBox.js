/**
 * A box with text and a button.
 * */ 
Ext.define('devilry_extjsextras.SingleActionBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.singleactionbox',
    cls: 'devilry_singleactionbox bootstrap',

    bodyTpl: '<p>{html}</p>',

    /**
     * @cfg {string} titleText (Required)
     */

    /**
     * @cfg {string} titleTpl (Optional)
     * Title template. Defaults to ``<strong>{text}</strong>``.
     */
    titleTpl: '<strong>{text}</strong>',

    /**
     * @cfg {string} bodyHtml (Required)
     */

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

    initComponent: function() {
        this.addEvents({
            /**
             * @event
             * Fired when clicking the button.
             * @param {devilry_extjsextras.SingleActionBox} singleactionbox
             * */
            click: true
        });
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
                    data: {
                        html: this.bodyHtml
                    },
                    padding: {right: 20},
                    columnWidth: 1
                }, {
                    xtype: 'button',
                    scale: this.buttonScale,
                    text: this.buttonText,
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
