Ext.define('devilry.extjshelpers.MaximizableWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.maximizablewindow',

    constructor: function(config) {
        this.callParent([config]);

        this.on('maximize', function() {
            window.scrollTo(0, 0);
        }, this);
    }
});
