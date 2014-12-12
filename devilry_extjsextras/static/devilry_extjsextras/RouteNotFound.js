Ext.define('devilry_extjsextras.RouteNotFound', {
    extend: 'Ext.Component',
    alias: 'widget.routenotfound',
    cls: 'bootstrap',
    
    tpl: [
        '<div class="alert alert-block error">',
        '  <h1 class="alert-heading">{title}</h1>',
        '  <p>{route}</p>',
        '  <div class="alert-actions">',
        '    <a class="btn" href="#">{gotodashboard}</a>',
        '  </div>',
        '</div>'
    ],

    data: {
        title: gettext('Route not found'),
        gotodashboard: gettext('Return to dashboard')
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
