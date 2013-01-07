/**
 * Mixin that can be used to automatically adjust the size of a component when the size
 * of the window changes.
 *
 * Example:
 *
 *      Ext.define('MyPanel', {
 *          constructor: function () {
 *              extends: 'Ext.panel.Panel',
 *              mixins: ['devilry_extjsextras.AutoHeightComponentMixin'],
 *              this.callParent(arguments);
 *              this.setupAutoHeightSizing();
 *          }
 *      });
 */
Ext.define('devilry_extjsextras.AutoHeightComponentMixin', {

    /**
     * @cfg {int} [autoHeightMargin=60]
     * The number of pixels to retract from the window height.
     */
    autoHeightMargin: 60,

    setupAutoHeightSizing: function() {
        Ext.fly(window).on('resize', function() {
            if(this.isVisible()) {
                this.setHeightAutomatically();
            }
        }, this);
        this.on('render', function() {
            this.setHeightAutomatically();
        }, this);
    },

    setHeightAutomatically: function() {
        var bodysize = Ext.getBody().getViewSize();
        var height = bodysize.height - this.autoHeightMargin;
        this.setHeight(height);
    }
});
