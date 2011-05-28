Ext.define('devilry.restful.PathRestProxy', {
    extend: 'Ext.data.proxy.Rest',
    buildUrl: function(request) {
        var path = request.operation.node.data.path;
        return '/restful/examiner/tree' + path + '/';
    }
});
