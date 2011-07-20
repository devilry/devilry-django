/** Panel to show StaticFeedback info .
 *
 * @xtype staticfeedbackeditableinfo
 */
Ext.define('devilry.extjshelpers.StaticFeedbackEditableInfo', {
    extend: 'devilry.extjshelpers.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditableinfo',

    constructor: function(config) {
        this.addEvents('clickNewFeedback');
        return this.callParent([config]);
    },

    initComponent: function() {

        var me = this;
        this.createButton = Ext.create('Ext.button.Button', {
            text: 'New feedback',
            margin: {left: 5},
            hidden: true,
            listeners: {
                click: function() {
                    me.fireEvent('clickNewFeedback');
                }
            }
        });
        this.addListener('afterStoreLoad', function() {
            this.getHeader().add(me.createButton);
        });
        this.callParent(arguments);
    },

    showNewFeedbackButton: function() {
        this.createButton.show();
    }
});
