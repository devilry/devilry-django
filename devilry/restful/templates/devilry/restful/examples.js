Ext.require('devilry.restful.view.assignments.Grid');
Ext.require('devilry.restful.model.Assignment');
Ext.require('devilry.restful.model.Subject');
Ext.require('devilry.restful.store.Assignments');


function ajaxGrid()
{
    // create the grid

    var grid = Ext.create('devilry.restful.view.assignments.Grid', {
        store: Ext.create('devilry.restful.store.Assignments', {
                    //pageSize: 5,
                    longnamefields: 1
               }),
        height: 300,
        width: 600,
        renderTo: 'grid-example',
        //columns: [
            //{header: 'Stuff', dataIndex: 'id', flex: 1},
            //{header: 'Name',  dataIndex: 'short_name',  flex: 1}]
    });

    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select an assignment',
        renderTo: 'simpleCombo',
        displayField: 'path',
        width: 400,
        labelWidth: 130,
        store: Ext.create('devilry.restful.store.Assignments'),
        queryMode: 'local',
        typeAhead: true
    });


    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select an assignment',
        renderTo: 'fancyCombo',
        displayField: 'path',
        width: 400,
        labelWidth: 130,
        //store: Ext.create('devilry.restful.store.Assignments', {pageSize:10}),
        store: Ext.create('devilry.restful.store.Assignments'),
        queryMode: 'remote',
        typeAhead: true,
        hideLabel: true,
        minChars: 3,
        hideTrigger:true,

        listConfig: {
            loadingText: 'Searching...',

            // Custom rendering template for each item
            getInnerTpl: function() {
                return '<div class="fancyComboItem">' +
                    '<div class="comboMain">{long_name}</div>' +
                    '<div class="comboSmall">{path}</div>' +
                '</div>';
            }
        },
        //pageSize: 10,
    });
}



function tree()
{
    Ext.define('PathRestProxy', {
        extend: 'Ext.data.proxy.Rest',
        buildUrl: function(request) {
            var path = request.operation.node.data.path;
            return '/restful/examiner/tree' + path + '/';
        }
    });

    Ext.define('SubjectTreeStore', {
        extend: 'Ext.data.TreeStore',
        model: 'devilry.restful.model.Subject',
        proxy: Ext.create('PathRestProxy', {
            type: 'ajax',
            url: '/restful/examiner/tree/',
            appendId: true,
            reader: {
                type: 'json',
                root: 'items'
            },
        }),
        root: {
            nodeType:'async',            
            short_name: 'Subjects',
            path: '',
            id: 0,
            expanded: true
        },
    });

    var store = Ext.create('SubjectTreeStore', {});
    //store.addListener('append', function(tree, parent, node, index) {
            //console.log(parent);
            //console.log(node);
            ////return this.parent.append(tree, parent, node, index);
        //});

    var tree = Ext.create('Ext.tree.Panel', {
        store: store,
        renderTo: 'subjecttree',
        height: 300,
        width: 250,
        title: 'Subjects',
        useArrows: true,
        columns: [{
                xtype: 'treecolumn',
                text: 'Name',
                dataIndex: 'short_name',
                width: 150
            }]
    });

}



Ext.onReady(function() {
    ajaxGrid();
    tree();
});

