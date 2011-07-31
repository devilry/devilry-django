Ext.define('devilry.extjshelpers.forms.Node', {
    extend: 'Ext.form.Panel',
    alias: 'widget.nodeform',
    cls: 'widget-nodeform',

    flex: 10,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: "short_name",
        fieldLabel: "Short name",
        xtype: 'textfield'
    }, {
        name: "long_name",
        fieldLabel: "Long name",
        xtype: 'textfield'
    //}, {
        //name: "parentnode",
        //fieldLabel: "Parent",
        //xtype: 'combobox',
        //valueField: 'id',
        //displayField: 'short_name',
        //listConfig: {
            //loadingText: 'Loading...',
            //emptyText: 'No matching items found.',
            //getInnerTpl: function() {
                //return '<div class="important">{short_name}</div><div class="unimportant">{long_name}</div>'
            //}
        //},
        //store: Ext.create('Ext.data.Store', {
            //model: Ext.define('devilry.extjshelpers.models.Node', {
                //extend: 'Ext.data.Model',
                //requires: ['devilry.extjshelpers.RestProxy'],
                //fields: [{
                    //"type": "int",
                    //"name": "id"
                //}, {
                    //"type": "auto",
                    //"name": "parentnode"
                //}, {
                    //"type": "auto",
                    //"name": "short_name"
                //}, {
                    //"type": "auto",
                    //"name": "long_name"
                //}],
                //idProperty: 'id',
                //proxy: Ext.create('devilry.extjshelpers.RestProxy', {
                    //url: '/administrator/restfulsimplifiednode/',
                    //extraParams: {
                        //getdata_in_qrystring: true
                    //},
                    //reader: {
                        //type: 'json',
                        //root: 'items',
                        //totalProperty: 'total'
                    //},
                    //writer: {
                        //type: 'json'
                    //}
                //})
            //}),
            //id: 'devilry.apps.administrator.simplified.SimplifiedNodeStoreCombo',
            //remoteFilter: true,
            //remoteSort: true,
            //autoSync: true
        //})
    }],

    help: '<p><strong>Choose a node</strong>. Students will be able to deliver after the node expires, however deliveries after the node will be clearly marked.</p><p>The <strong>text</strong> is displayed to students when they view the node, and when they add deliveries on the node.</p>',
});
