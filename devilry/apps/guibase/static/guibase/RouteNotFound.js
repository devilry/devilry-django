Ext.define('guibase.RouteNotFound', {
    extend: 'Ext.Component',
    alias: 'widget.routenotfound',
    
    tpl: [
        '<div class="alert-message block-message error">',
        '  <h1>Route not found</h1>',
        '  <p>The following route is not available: <strong>{route}</strong></p>',
        '  <div class="alert-actions">',
        '    <a class="btn small" href="#">Go to dashboard</a>',
        '  </div>',
        '</div>'
    ]
});
