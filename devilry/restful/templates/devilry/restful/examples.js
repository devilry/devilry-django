Ext.require('devilry.restful.view.assignments.Grid');
Ext.require('devilry.restful.model.Assignment');
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
    var store = Ext.create('Ext.data.TreeStore', {
        proxy: {
            type: 'ajax',
            url: '/restful/examiner/assignments/'
        },
        root: {
            text: 'root',
            id: 'src',
            expanded: true
        }
    });

    var tree = Ext.create('Ext.tree.Panel', {
        store: store,
        viewConfig: {
            plugins: {
                ptype: 'treeviewdragdrop'
            }
        },
        renderTo: 'tree-div',
        height: 300,
        width: 250,
        title: 'Files',
        useArrows: true,
        dockedItems: [{
            xtype: 'toolbar',
            items: [{
                text: 'Expand All',
                handler: function(){
                    tree.expandAll();
                }
            }, {
                text: 'Collapse All',
                handler: function(){
                    tree.collapseAll();
                }
            }]
        }]
    });

}



Ext.onReady(function() {
    ajaxGrid();
    tree();
});

