/** Panel to show StaticFeedback info:
 *
 * @xtype staticfeedbackinfo
 */
Ext.define('devilry.extjshelpers.StaticFeedbackInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.staticfeedbackinfo',
    title: 'Feedback',

    config: {
        /**
         * @cfg
         * StaticFeedbackInfo record as returned from loading it by id as a model.
         */
        staticfeedback: undefined
    },

    initComponent: function() {
        Ext.apply(this, {
            
        });

        this.callParent(arguments);
    }
});
