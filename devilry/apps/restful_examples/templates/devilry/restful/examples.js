Ext.require('devilry.restful.view.assignments.Grid');
Ext.require('devilry.restful.PathRestProxy');
Ext.require('devilry.restful.store.SubjectTree');
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



function subjectTree() {

    var store = Ext.create('devilry.restful.store.SubjectTree');

    var subjectTree = Ext.create('Ext.tree.Panel', {
        store: store,
        renderTo: 'subjecttree',
        height: 300,
        width: 250,
        title: 'Subjects',
        useArrows: true,
        rootVisible: false,
        columns: [{
                xtype: 'treecolumn',
                text: 'Name',
                dataIndex: 'short_name',
                width: 150
            }]
    });

    subjectTree.addListener('itemclick', function(t, record, item, index, e) {
        var data = record.data;
        if(data.leaf) {
            console.log(data);
        }
    });

}


function subjectForm() {
    Ext.define('example.fielderror', {
        extend: 'Ext.data.Model',
        fields: ['id', 'msg']
    });

    var formPanel = Ext.create('Ext.form.Panel', {
        renderTo: 'subjectform',
        frame: true,
        title: 'Subject Form',
        width: 340,
        bodyPadding: 5,
        waitMsgTarget: true,

        fieldDefaults: {
            labelAlign: 'right',
            labelWidth: 85,
            msgTarget: 'side'
        },

        // configure how to read the XML data
        reader: Ext.create('Ext.data.reader.Json', {
            model: 'devilry.restful.model.Subject',
            root: 'items',
            successProperty: 'success'
        }),

        // configure how to read the XML errors
        //errorReader: Ext.create('Ext.data.reader.Xml', {
            //model: 'example.fielderror',
            //record: 'field',
            //successProperty: '@success'
        //}),

        items: [{
            xtype: 'fieldset',
            title: 'Contact Information',
            defaultType: 'textfield',
            defaults: {
                width: 280
            },
            items: [{
                fieldLabel: 'Short name',
                emptyText: 'duck1010',
                name: 'short_name'
            }, {
                fieldLabel: 'Long name',
                emptyText: 'Learning to fly',
                name: 'long_name'
            }]
        }],

        buttons: [{
            text: 'Load',
            handler: function() {
                formPanel.getForm().load({
                    url: 'xml-form-data.xml',
                    waitMsg: 'Loading...'
                });
            }
        }, {
            text: 'Submit',
            disabled: true,
            formBind: true,
            handler: function() {
                this.up('form').getForm().submit({
                    url: 'xml-form-errors.xml',
                    submitEmptyText: false,
                    waitMsg: 'Saving Data...'
                });
            }
        }]
    });
}



Ext.onReady(function() {
    ajaxGrid();
    subjectTree();
    subjectForm();
});

