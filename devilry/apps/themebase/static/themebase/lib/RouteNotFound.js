Ext.define('themebase.RouteNotFound', {
    extend: 'Ext.Component',
    alias: 'widget.routenotfound',
    
    tpl: [
        '<div class="alert-message block-message error">',
        '  <h1>{title}</h1>',
        '  <p>{route}</p>',
        '  <div class="alert-actions">',
        '    <a class="btn small" href="#">{gotodashboard}</a>',
        '  </div>',
        '</div>'
    ],

    data: {
        title: dtranslate('themebase.routenotfound'),
        gotodashboard: dtranslate('themebase.gotodashboard')
    },

    /**
     * @cfg
     * The missed route.
     */
    route: undefined,

    initComponent: function() {
        this.data.route = this.route;
        this.callParent(arguments);
    }
});
