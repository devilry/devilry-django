Ext.define('guibase.RouteNotFound', {
    extend: 'Ext.Component',
    alias: 'widget.routenotfound',
    
    tpl: [
        '<h1>Route not found</h1>',
        '<p>The following route is not available: <strong>{route}</strong></p>'
    ]
});
