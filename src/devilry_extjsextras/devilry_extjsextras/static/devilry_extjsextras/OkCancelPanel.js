Ext.define('devilry_extjsextras.OkCancelPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.okcancelpanel',
    cls: 'devilry_extjsextras_okcancelpanel bootstrap',

    /**
     * @cfg {String} [oktext]
     * The text of the OK button. Defauls to "Ok" translated.
     */
    oktext: pgettext('uibutton', 'Ok'),

    /**
     * @cfg {String} [canceltext]
     * The text of the Cancel button. Defauls to "Cancel" translated.
     */
    canceltext: gettext('Cancel'),

    /**
     * @cfg {String} [okbutton_ui="primary"]
     * The ``ui``-config for the OK-button.
     */
    okbutton_ui: 'primary',

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            /** @event
             * Fired when the OK-button is clicked.
             * @param panel This panel.
             */
            'ok',

            /** @event
             * Fired when the Cancel-button is clicked.
             * @param panel This panel.
             */
            'cancel'
        );
    },

    
    initComponent: function() {
        Ext.apply(this, {
            fbar: [{
                xtype: 'button',
                itemId: 'cancelbutton',
                cls: 'cancelbutton',
                text: this.canceltext,
                listeners: {
                    scope: this,
                    click: this._onCancelButtonClick
                }
            }, {
                xtype: 'button',
                itemId: 'okbutton',
                ui: this.okbutton_ui,
                scale: 'large',
                cls: 'okbutton',
                text: this.oktext,
                listeners: {
                    scope: this,
                    click: this._onOkButtonClick
                }
            }]
        });
        this.callParent(arguments);
    },

    _onCancelButtonClick: function() {
        this.fireEvent('cancel', this);
    },

    _onOkButtonClick: function() {
        this.fireEvent('ok', this);
    }
});
