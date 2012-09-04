Ext.define('devilry_extjsextras.OkCancelPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.okcancelpanel',
    cls: 'devilry_extjsextras_okcancelpanel',

    /**
     * @cfg {String} [oktext]
     * The text of the OK button. Defauls to "Ok" translated.
     */
    oktext: gettext('Ok'),

    /**
     * @cfg {String} [canceltext]
     * The text of the Cancel button. Defauls to "Cancel" translated.
     */
    canceltext: gettext('Cancel'),

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
                text: this.canceltext,
                listeners: {
                    scope: this,
                    click: this._onCancelButtonClick
                }
            }, {
                xtype: 'primarybutton',
                itemId: 'okbutton',
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
