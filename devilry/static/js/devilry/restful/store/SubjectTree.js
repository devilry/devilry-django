Ext.define('devilry.restful.store.SubjectTree', {
    extend: 'Ext.data.TreeStore',
    requires: ['devilry.restful.model.SubjectTree'],
    model: 'devilry.restful.model.SubjectTree',
    root: {
        nodeType:'async',            
        short_name: 'Subjects',
        path: '',
        id: 0,
        expanded: true
    },

    proxy: Ext.create('devilry.restful.PathRestProxy', {
        type: 'ajax',
        url: '/restful/examiner/tree/',
        appendId: true,
        reader: {
            type: 'json',
            root: 'items'
        },
    }),

    listeners: {
        append: {
            fn: function(tree, parent, node, index) {
                var path = parent.data.path;
                var depth = path.split('/').length - 1;
                if(depth == 3) {
                    parent.data.leaf = true;
                }
            }
        }
    }
});
